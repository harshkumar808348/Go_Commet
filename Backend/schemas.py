"""
Pydantic schemas for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Request Schemas ──────────────────────────────────────────────

class ScoreSubmission(BaseModel):
    """Request body for submitting a score."""

    user_id: int = Field(..., gt=0, description="ID of the player")
    score: int = Field(..., gt=0, description="Score achieved in the game session")
    game_mode: str = Field(default="solo", description="Game mode: 'solo' or 'team'")


# ── Response Schemas ─────────────────────────────────────────────

class SubmitResponse(BaseModel):
    """Response after successfully submitting a score."""

    message: str
    user_id: int
    new_total_score: int
    new_rank: Optional[int] = None


class LeaderboardEntry(BaseModel):
    """A single entry in the leaderboard response."""

    rank: int
    user_id: int
    username: str
    total_score: int


class LeaderboardResponse(BaseModel):
    """Response containing the top players list."""

    leaderboard: list[LeaderboardEntry]
    updated_at: datetime


class PlayerRankResponse(BaseModel):
    """Response for a player's rank lookup."""

    user_id: int
    username: str
    total_score: int
    rank: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
