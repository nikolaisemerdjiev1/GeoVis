from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import (
    ConfusionEntryOut,
    CountryPerformanceOut,
    GameIn,
    GameSummaryOut,
    ImportEventOut,
    PracticeRecommendationOut,
    RegionConfusionEntryOut,
    RegionPerformanceOut,
    ReviewOptionOut,
    ReviewQueueOut,
    RoundNoteIn,
    RoundReviewOut,
    ScoreTrendEntryOut,
)
from ..services.export import create_sqlite_backup
from ..services.analytics import (
    get_confusion_matrix,
    get_country_performance,
    get_recent_games,
    get_region_confusion_matrix,
    get_region_performance,
    get_score_trend,
)
from ..services.ingest import create_game, get_recent_import_events
from ..services.recommender import get_practice_priorities, get_review_queue
from ..services.round_review import get_review_options, get_round_reviews, upsert_round_note

router = APIRouter(prefix="/api", tags=["geovis"])


@router.post("/ingest/game", response_model=GameSummaryOut)
def ingest_game(payload: GameIn, db: Session = Depends(get_db)):
    game, _status = create_game(db, payload)
    return game


@router.get("/games/recent", response_model=list[GameSummaryOut])
def recent_games(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return get_recent_games(db, limit=limit)


@router.get("/imports/recent", response_model=list[ImportEventOut])
def recent_imports(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return get_recent_import_events(db, limit=limit)


@router.get("/export/sqlite")
def export_sqlite_backup():
    backup_path = create_sqlite_backup()
    return FileResponse(
        backup_path,
        media_type="application/vnd.sqlite3",
        filename=backup_path.name,
    )


@router.get("/analytics/country-performance", response_model=list[CountryPerformanceOut])
def country_performance(db: Session = Depends(get_db)):
    return get_country_performance(db)


@router.get("/analytics/region-performance", response_model=list[RegionPerformanceOut])
def region_performance(db: Session = Depends(get_db)):
    return get_region_performance(db)


@router.get("/analytics/confusion-matrix", response_model=list[ConfusionEntryOut])
def confusion_matrix(limit: int = 100, db: Session = Depends(get_db)):
    return get_confusion_matrix(db, limit=limit)


@router.get("/analytics/region-confusion-matrix", response_model=list[RegionConfusionEntryOut])
def region_confusion_matrix(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    return get_region_confusion_matrix(db, limit=limit)


@router.get("/analytics/score-trend", response_model=list[ScoreTrendEntryOut])
def score_trend(limit: int = 100, db: Session = Depends(get_db)):
    return get_score_trend(db, limit=limit)


@router.get("/analytics/practice-priorities", response_model=list[PracticeRecommendationOut])
def practice_priorities(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return get_practice_priorities(db, limit=limit)


@router.get("/training/review-queue", response_model=ReviewQueueOut)
def review_queue(limit: int = Query(default=12, ge=1, le=50), db: Session = Depends(get_db)):
    return get_review_queue(db, limit=limit)


@router.get("/rounds/review", response_model=list[RoundReviewOut])
def round_reviews(
    limit: int = Query(default=100, ge=1, le=500),
    mistake_type: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    reviewed: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_round_reviews(
        db,
        limit=limit,
        mistake_type=mistake_type,
        tag=tag,
        reviewed=reviewed,
    )


@router.put("/rounds/{round_id}/note", response_model=RoundReviewOut)
def update_round_note(round_id: int, payload: RoundNoteIn, db: Session = Depends(get_db)):
    review = upsert_round_note(db, round_id, payload)
    if review is None:
        raise HTTPException(status_code=404, detail="Round not found")
    return review


@router.get("/rounds/review/options", response_model=ReviewOptionOut)
def round_review_options(db: Session = Depends(get_db)):
    return get_review_options(db)
