"""
Database seeding script for the Gaming Leaderboard.

Populates the database with:
  - 1,000,000 users
  - 5,000,000 game sessions (random scores & modes)
  - Aggregated leaderboard entries with ranks

Usage:
    python seed_db.py
"""

import time
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:123456789@localhost:5432/Commet"
engine = create_engine(DATABASE_URL)


def seed():
    """Run all seeding steps sequentially."""
    with engine.connect() as conn:
        # ── Step 0: Clean Slate ──────────────────────────────────
        print("⏳ Cleaning existing data...")
        conn.execute(text("TRUNCATE TABLE users, game_sessions, leaderboard RESTART IDENTITY CASCADE"))
        conn.commit()

        # ── Step 1: Users ────────────────────────────────────────
        print("⏳ Inserting 1,000,000 users …")
        start = time.time()
        conn.execute(text("""
            INSERT INTO users (username)
            SELECT 'user_' || generate_series(1, 1000000)
            ON CONFLICT (username) DO NOTHING
        """))
        conn.commit()
        print(f"   ✓ Users inserted in {time.time() - start:.1f}s")

        # ── Step 2: Game Sessions ────────────────────────────────
        print("⏳ Inserting 5,000,000 game sessions …")
        start = time.time()
        conn.execute(text("""
            INSERT INTO game_sessions (user_id, score, game_mode, timestamp)
            SELECT
                floor(random() * 1000000 + 1)::int,
                floor(random() * 10000 + 1)::int,
                CASE WHEN random() > 0.5 THEN 'solo' ELSE 'team' END,
                NOW() - INTERVAL '1 day' * floor(random() * 365)
            FROM generate_series(1, 5000000)
        """))
        conn.commit()
        print(f"   ✓ Game sessions inserted in {time.time() - start:.1f}s")

        # ── Step 3: Leaderboard ──────────────────────────────────
        print("⏳ Aggregating leaderboard …")
        start = time.time()
        conn.execute(text("DELETE FROM leaderboard"))
        conn.execute(text("""
            INSERT INTO leaderboard (user_id, total_score, rank)
            SELECT
                user_id,
                SUM(score)::int AS total_score,
                RANK() OVER (ORDER BY SUM(score) DESC)
            FROM game_sessions
            GROUP BY user_id
        """))
        conn.commit()
        print(f"   ✓ Leaderboard aggregated in {time.time() - start:.1f}s")

    print("\n🎉 Database seeding complete!")


if __name__ == "__main__":
    seed()
