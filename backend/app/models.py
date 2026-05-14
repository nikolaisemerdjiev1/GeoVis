from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_game_id: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    played_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    mode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    map_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    total_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    rounds_count: Mapped[int] = mapped_column(Integer, default=0)
    result_text: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rating_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rounds: Mapped[list[Round]] = relationship(
        "Round", back_populates="game", cascade="all, delete-orphan"
    )
    import_events: Mapped[list[ImportEvent]] = relationship("ImportEvent", back_populates="game")


class ImportEvent(Base):
    __tablename__ = "import_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_game_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    game_id: Mapped[int | None] = mapped_column(ForeignKey("games.id", ondelete="SET NULL"), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    game: Mapped[Game | None] = relationship("Game", back_populates="import_events")


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    round_number: Mapped[int] = mapped_column(Integer, index=True)
    actual_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    guess_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    guess_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_country: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    guessed_country: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    actual_region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    guessed_region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    guess_time_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    movement_allowed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    timer_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)

    game: Mapped[Game] = relationship("Game", back_populates="rounds")
    note: Mapped[RoundNote | None] = relationship(
        "RoundNote", back_populates="round", cascade="all, delete-orphan", uselist=False
    )


class RoundNote(Base):
    __tablename__ = "round_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id", ondelete="CASCADE"), unique=True)
    mistake_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    manual_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)

    round: Mapped[Round] = relationship("Round", back_populates="note")
