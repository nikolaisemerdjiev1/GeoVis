from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RoundIn(BaseModel):
    round_number: int
    actual_lat: float | None = None
    actual_lng: float | None = None
    guess_lat: float | None = None
    guess_lng: float | None = None
    actual_country: str | None = None
    guessed_country: str | None = None
    actual_region: str | None = None
    guessed_region: str | None = None
    distance_km: float | None = None
    score: int | None = None
    guess_time_sec: float | None = None
    movement_allowed: bool | None = None
    timer_sec: int | None = None


class GameIn(BaseModel):
    game_id: str | None = Field(default=None, alias="external_game_id")
    played_at: datetime
    mode: str | None = None
    map_name: str | None = None
    total_score: int | None = None
    total_distance_km: float | None = None
    result_text: str | None = None
    rating_before: int | None = None
    rating_after: int | None = None
    rounds: list[RoundIn]

    model_config = {"populate_by_name": True}


class GameSummaryOut(BaseModel):
    id: int
    external_game_id: str | None
    played_at: datetime
    mode: str | None
    map_name: str | None
    total_score: int | None
    total_distance_km: float | None
    rounds_count: int
    result_text: str | None
    rating_before: int | None
    rating_after: int | None

    model_config = {"from_attributes": True}


class CountryPerformanceOut(BaseModel):
    actual_country: str
    rounds_played: int
    avg_score: float | None
    median_distance_km: float | None
    avg_distance_km: float | None
    correct_country_rate: float | None


class ConfusionEntryOut(BaseModel):
    actual_country: str
    guessed_country: str
    count: int


class ScoreTrendEntryOut(BaseModel):
    played_at: datetime
    total_score: int | None
    map_name: str | None
    mode: str | None
