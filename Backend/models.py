"""
SQLAlchemy ORM models for the Gaming Leaderboard system.
Tables: users, game_sessions, leaderboard
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """Represents a registered player."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    join_date = Column(DateTime, server_default=func.now())

    # Relationships
    game_sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    leaderboard_entry = relationship("Leaderboard", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class GameSession(Base):
    """Records an individual game session with score and mode."""

    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    game_mode = Column(String(50), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="game_sessions")

    def __repr__(self):
        return f"<GameSession(id={self.id}, user_id={self.user_id}, score={self.score})>"


class Leaderboard(Base):
    """Aggregated leaderboard entry per user with total score and rank."""

    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_score = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="leaderboard_entry")

    def __repr__(self):
        return f"<Leaderboard(user_id={self.user_id}, total_score={self.total_score}, rank={self.rank})>"
