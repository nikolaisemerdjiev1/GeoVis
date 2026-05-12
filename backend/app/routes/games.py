from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import (
    ConfusionEntryOut,
    CountryPerformanceOut,
    GameIn,
    GameSummaryOut,
    ScoreTrendEntryOut,
)
from ..services.analytics import (
    get_confusion_matrix,
    get_country_performance,
    get_recent_games,
    get_score_trend,
)
from ..services.ingest import create_game
from ..services.recommender import get_practice_priorities

router = APIRouter(prefix="/api", tags=["geovis"])


@router.post("/ingest/game", response_model=GameSummaryOut)
def ingest_game(payload: GameIn, db: Session = Depends(get_db)):
    game = create_game(db, payload)
    return game


@router.get("/games/recent", response_model=list[GameSummaryOut])
def recent_games(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return get_recent_games(db, limit=limit)


@router.get("/analytics/country-performance", response_model=list[CountryPerformanceOut])
def country_performance(db: Session = Depends(get_db)):
    return get_country_performance(db)


@router.get("/analytics/confusion-matrix", response_model=list[ConfusionEntryOut])
def confusion_matrix(limit: int = 100, db: Session = Depends(get_db)):
    return get_confusion_matrix(db, limit=limit)


@router.get("/analytics/score-trend", response_model=list[ScoreTrendEntryOut])
def score_trend(limit: int = 100, db: Session = Depends(get_db)):
    return get_score_trend(db, limit=limit)


@router.get("/analytics/practice-priorities")
def practice_priorities(db: Session = Depends(get_db)):
    return get_practice_priorities(db)
