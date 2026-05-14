from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas


def log_import_event(
    db: Session,
    *,
    external_game_id: str | None,
    status: str,
    source: str = "extension",
    message: str | None = None,
    game_id: int | None = None,
    commit: bool = True,
) -> models.ImportEvent:
    event = models.ImportEvent(
        external_game_id=external_game_id,
        game_id=game_id,
        status=status,
        source=source,
        message=message,
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    return event


def create_game(db: Session, payload: schemas.GameIn) -> tuple[models.Game, str]:
    existing = None
    if payload.game_id:
        existing = (
            db.query(models.Game)
            .filter(models.Game.external_game_id == payload.game_id)
            .first()
        )
    if existing:
        log_import_event(
            db,
            external_game_id=payload.game_id,
            status="duplicate",
            message="Game already imported",
            game_id=existing.id,
        )
        return existing, "duplicate"

    game = models.Game(
        external_game_id=payload.game_id,
        played_at=payload.played_at,
        mode=payload.mode,
        map_name=payload.map_name,
        total_score=payload.total_score,
        total_distance_km=payload.total_distance_km,
        result_text=payload.result_text,
        rating_before=payload.rating_before,
        rating_after=payload.rating_after,
        rounds_count=len(payload.rounds),
    )
    db.add(game)
    db.flush()

    for round_payload in payload.rounds:
        round_row = models.Round(
            game_id=game.id,
            round_number=round_payload.round_number,
            actual_lat=round_payload.actual_lat,
            actual_lng=round_payload.actual_lng,
            guess_lat=round_payload.guess_lat,
            guess_lng=round_payload.guess_lng,
            actual_country=round_payload.actual_country,
            guessed_country=round_payload.guessed_country,
            actual_region=round_payload.actual_region,
            guessed_region=round_payload.guessed_region,
            distance_km=round_payload.distance_km,
            score=round_payload.score,
            guess_time_sec=round_payload.guess_time_sec,
            movement_allowed=round_payload.movement_allowed,
            timer_sec=round_payload.timer_sec,
        )
        db.add(round_row)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if payload.game_id:
            existing = (
                db.query(models.Game)
                .filter(models.Game.external_game_id == payload.game_id)
                .first()
            )
            if existing:
                log_import_event(
                    db,
                    external_game_id=payload.game_id,
                    status="duplicate",
                    message="Game already imported",
                    game_id=existing.id,
                )
                return existing, "duplicate"
        raise
    except Exception as exc:
        db.rollback()
        log_import_event(
            db,
            external_game_id=payload.game_id,
            status="error",
            message=str(exc),
        )
        raise

    db.refresh(game)
    log_import_event(
        db,
        external_game_id=payload.game_id,
        status="success",
        message=f"Imported {len(payload.rounds)} rounds",
        game_id=game.id,
    )
    return game, "success"


def get_recent_import_events(db: Session, limit: int = 20) -> list[models.ImportEvent]:
    return (
        db.query(models.ImportEvent)
        .order_by(models.ImportEvent.created_at.desc())
        .limit(limit)
        .all()
    )
