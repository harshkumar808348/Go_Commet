"""
Leaderboard API routes with caching, indexing, and atomic transactions.

Endpoints:
  POST /api/leaderboard/submit    — Submit a game score
  GET  /api/leaderboard/top       — Get top 10 players
  GET  /api/leaderboard/rank/{id} — Get a player's rank
"""

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from limiter import limiter
from schemas import (
    ScoreSubmission,
    SubmitResponse,
    LeaderboardResponse,
    LeaderboardEntry,
    PlayerRankResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])

# ── Redis helper (graceful fallback if unavailable) ──────────────

_redis_client = None


def get_redis():
    """Lazy-initialize and return the Redis client, or None if unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis

        _redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        _redis_client.ping()
        logger.info("✓ Redis connected — caching is enabled")
        return _redis_client
    except Exception:
        logger.warning("⚠ Redis unavailable — running without cache")
        _redis_client = None
        return None


def cache_get(key: str):
    """Read a JSON value from Redis; returns None on miss or if Redis is down."""
    r = get_redis()
    if r is None:
        return None
    try:
        data = r.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


def cache_set(key: str, value, ttl: int = 5):
    """Write a JSON value to Redis with a TTL (seconds)."""
    r = get_redis()
    if r is None:
        return
    try:
        r.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def cache_invalidate(*keys: str):
    """Delete one or more cache keys."""
    r = get_redis()
    if r is None:
        return
    try:
        r.delete(*keys)
    except Exception:
        pass


# ── Dependency ───────────────────────────────────────────────────

def get_db():
    """Import the session factory from app.py and yield a session."""
    from app import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── 1. Submit Score ──────────────────────────────────────────────

@router.post("/submit", response_model=SubmitResponse)
@limiter.limit("5/minute")
def submit_score(request: Request, payload: ScoreSubmission, db: Session = Depends(get_db)):
    """
    Submit a game score for a player.

    Steps (inside a single transaction):
      1. Verify user exists
      2. Insert a new game_session row
      3. Upsert the leaderboard entry (sum scores, recalculate rank)
    """
    try:
        # --- Begin atomic transaction --------------------------------
        # 1. Validate user
        user = db.execute(
            text("SELECT id, username FROM users WHERE id = :uid"),
            {"uid": payload.user_id},
        ).fetchone()

        if not user:
            raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

        # 2. Insert game session
        db.execute(
            text(
                "INSERT INTO game_sessions (user_id, score, game_mode) "
                "VALUES (:uid, :score, :mode)"
            ),
            {"uid": payload.user_id, "score": payload.score, "mode": payload.game_mode},
        )

        # 3. Upsert leaderboard entry (atomic)
        db.execute(
            text(
                """
                INSERT INTO leaderboard (user_id, total_score, rank)
                VALUES (:uid, :score, 0)
                ON CONFLICT (user_id)
                DO UPDATE SET total_score = leaderboard.total_score + :score
                """
            ),
            {"uid": payload.user_id, "score": payload.score},
        )

        # 4. Fetch updated total
        row = db.execute(
            text("SELECT total_score FROM leaderboard WHERE user_id = :uid"),
            {"uid": payload.user_id},
        ).fetchone()

        new_total = row[0] if row else payload.score

        # 5. Recalculate rank for this user only (lightweight)
        rank_row = db.execute(
            text(
                """
                SELECT COUNT(*) + 1
                FROM leaderboard
                WHERE total_score > :total
                """
            ),
            {"total": new_total},
        ).fetchone()

        new_rank = rank_row[0] if rank_row else 1

        # Update rank
        db.execute(
            text("UPDATE leaderboard SET rank = :rank WHERE user_id = :uid"),
            {"rank": new_rank, "uid": payload.user_id},
        )

        db.commit()
        # --- End atomic transaction ----------------------------------

        # Invalidate caches so next reads reflect the new data
        cache_invalidate("leaderboard:top10", f"rank:{payload.user_id}")

        logger.info("Score %d submitted for user %d (total=%d, rank=%d)",
                     payload.score, payload.user_id, new_total, new_rank)

        return SubmitResponse(
            message="Score submitted successfully",
            user_id=payload.user_id,
            new_total_score=new_total,
            new_rank=new_rank,
        )

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("submit_score failed: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


# ── 2. Get Leaderboard (Top 10) ─────────────────────────────────

@router.get("/top", response_model=LeaderboardResponse)
@limiter.limit("60/minute")
def get_leaderboard(request: Request, db: Session = Depends(get_db)):
    """Return the top 10 players, sorted by total_score descending."""

    # Try cache first
    cached = cache_get("leaderboard:top10")
    if cached:
        return LeaderboardResponse(**cached)

    rows = db.execute(
        text(
            """
            SELECT l.rank, l.user_id, u.username, l.total_score
            FROM leaderboard l
            JOIN users u ON u.id = l.user_id
            ORDER BY l.total_score DESC
            LIMIT 10
            """
        )
    ).fetchall()

    entries = [
        LeaderboardEntry(rank=idx + 1, user_id=r[1], username=r[2], total_score=r[3])
        for idx, r in enumerate(rows)
    ]

    response = LeaderboardResponse(
        leaderboard=entries,
        updated_at=datetime.now(timezone.utc),
    )

    # Cache for 5 seconds
    cache_set("leaderboard:top10", response.model_dump())

    return response


# ── 3. Get Player Rank ──────────────────────────────────────────

@router.get("/rank/{user_id}", response_model=PlayerRankResponse)
@limiter.limit("60/minute")
def get_player_rank(request: Request, user_id: int, db: Session = Depends(get_db)):
    """Fetch a specific player's rank and total score."""

    # Try cache first
    cache_key = f"rank:{user_id}"
    cached = cache_get(cache_key)
    if cached:
        return PlayerRankResponse(**cached)

    row = db.execute(
        text(
            """
            SELECT
                l.user_id,
                u.username,
                l.total_score,
                (SELECT COUNT(*) + 1 FROM leaderboard WHERE total_score > l.total_score) AS computed_rank
            FROM leaderboard l
            JOIN users u ON u.id = l.user_id
            WHERE l.user_id = :uid
            """
        ),
        {"uid": user_id},
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"No leaderboard entry for user {user_id}")

    response = PlayerRankResponse(
        user_id=row[0],
        username=row[1],
        total_score=row[2],
        rank=row[3],
    )

    # Cache for 5 seconds
    cache_set(cache_key, response.model_dump())

    return response
