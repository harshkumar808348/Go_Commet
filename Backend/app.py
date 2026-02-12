"""
Gaming Leaderboard — FastAPI Application Entry Point.

Provides a high-performance leaderboard system with:
  - Score submission with atomic transactions
  - Cached leaderboard and rank queries
  - Database indexing for optimized reads
  - CORS support for the React frontend
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter import limiter
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models import Base
from routes import router as leaderboard_router

# ── Logging ──────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
)
logger = logging.getLogger(__name__)

# ── Database ─────────────────────────────────────────────────────

DATABASE_URL = "postgresql://postgres:123456789@localhost:5432/Commet"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _create_tables():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables ensured")


def _create_indexes():
    """Create performance indexes (idempotent — uses IF NOT EXISTS)."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_gs_user_id       ON game_sessions (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_lb_total_score    ON leaderboard  (total_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_lb_user_id        ON leaderboard  (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_lb_rank           ON leaderboard  (rank)",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_lb_user_unique ON leaderboard (user_id)",
    ]
    with engine.connect() as conn:
        for stmt in indexes:
            conn.execute(text(stmt))
        conn.commit()
    logger.info("✓ Database indexes ensured")


# ── App Lifecycle ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle handler."""
    # Startup
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connected successfully")
    except Exception as e:
        logger.error("✗ Database connection failed: %s", e)

    _create_tables()
    _create_indexes()

    yield  # ← app is running

    # Shutdown
    engine.dispose()
    logger.info("Database connections closed")


# ── FastAPI App ──────────────────────────────────────────────────

# ── New Relic (Monitoring) ───────────────────────────────────────
try:
    import newrelic.agent
    newrelic.agent.initialize("newrelic.ini")
    logger.info("✓ New Relic agent initialized")
except Exception:
    logger.warning("⚠ New Relic agent skipped (ensure newrelic.ini exists and dependency installed)")

app = FastAPI(
    title="Gaming Leaderboard API",
    description="High-performance leaderboard with caching, indexing, and atomic writes",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(leaderboard_router)


# ── Health Check ─────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "service": "gaming-leaderboard"}


if __name__ == "__main__":
    import uvicorn
    # Run the app with auto-reload enabled
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)