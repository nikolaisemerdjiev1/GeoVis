from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class RoundIn(BaseModel):
    round_number: int = Field(ge=1, le=100)
    actual_lat: float | None = Field(default=None, ge=-90, le=90)
    actual_lng: float | None = Field(default=None, ge=-180, le=180)
    guess_lat: float | None = Field(default=None, ge=-90, le=90)
    guess_lng: float | None = Field(default=None, ge=-180, le=180)
    actual_country: str | None = None
    guessed_country: str | None = None
    actual_region: str | None = None
    guessed_region: str | None = None
    distance_km: float | None = Field(default=None, ge=0)
    score: int | None = Field(default=None, ge=0, le=5000)
    guess_time_sec: float | None = Field(default=None, ge=0)
    movement_allowed: bool | None = None
    timer_sec: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def has_result_signal(self) -> "RoundIn":
        if self.score is None and self.distance_km is None and self.guess_lat is None and self.guess_lng is None:
            raise ValueError("round must include a completed-result signal")
        return self


class GameIn(BaseModel):
    game_id: str | None = Field(default=None, alias="external_game_id")
    played_at: datetime
    mode: str | None = None
    map_name: str | None = None
    total_score: int | None = Field(default=None, ge=0, le=50000)
    total_distance_km: float | None = Field(default=None, ge=0)
    result_text: str | None = None
    rating_before: int | None = Field(default=None, ge=0)
    rating_after: int | None = Field(default=None, ge=0)
    rounds: list[RoundIn] = Field(min_length=1, max_length=100)

    model_config = {"populate_by_name": True}

    @field_validator("game_id", "mode", "map_name", "result_text")
    @classmethod
    def clean_blank_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


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
