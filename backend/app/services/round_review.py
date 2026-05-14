from __future__ import annotations

import json

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas


def encode_tags(tags: list[str]) -> str:
    return json.dumps(tags, separators=(",", ":"))


def decode_tags(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = [item.strip() for item in value.split(",")]
    if not isinstance(parsed, list):
        return []
    return [str(item).strip().lower() for item in parsed if str(item).strip()]


def note_reviewed(note: models.RoundNote | None) -> bool:
    if note is None:
        return False
    return bool(note.mistake_type or note.manual_notes or decode_tags(note.tags))


def round_to_review(row: models.Round) -> schemas.RoundReviewOut:
    note = row.note
    return schemas.RoundReviewOut(
        id=row.id,
        game_id=row.game_id,
        external_game_id=row.game.external_game_id,
        played_at=row.game.played_at,
        map_name=row.game.map_name,
        mode=row.game.mode,
        round_number=row.round_number,
        actual_country=row.actual_country,
        guessed_country=row.guessed_country,
        actual_region=row.actual_region,
        guessed_region=row.guessed_region,
        distance_km=row.distance_km,
        score=row.score,
        mistake_type=note.mistake_type if note else None,
        manual_notes=note.manual_notes if note else None,
        tags=decode_tags(note.tags if note else None),
        reviewed=note_reviewed(note),
    )


def get_round_reviews(
    db: Session,
    *,
    limit: int = 100,
    mistake_type: str | None = None,
    tag: str | None = None,
    reviewed: bool | None = None,
) -> list[schemas.RoundReviewOut]:
    query = (
        db.query(models.Round)
        .join(models.Game)
        .options(joinedload(models.Round.game), joinedload(models.Round.note))
        .order_by(desc(models.Game.played_at), models.Round.round_number.asc())
    )

    rows = query.all()
    output = [round_to_review(row) for row in rows]

    if mistake_type:
        wanted = mistake_type.strip().lower()
        output = [row for row in output if (row.mistake_type or "").lower() == wanted]
    if tag:
        wanted_tag = tag.strip().lower()
        output = [row for row in output if wanted_tag in row.tags]
    if reviewed is not None:
        output = [row for row in output if row.reviewed is reviewed]

    return output[:limit]


def upsert_round_note(db: Session, round_id: int, payload: schemas.RoundNoteIn) -> schemas.RoundReviewOut | None:
    round_row = (
        db.query(models.Round)
        .options(joinedload(models.Round.game), joinedload(models.Round.note))
        .filter(models.Round.id == round_id)
        .first()
    )
    if round_row is None:
        return None

    note = round_row.note
    if note is None:
        note = models.RoundNote(round_id=round_id)
        db.add(note)

    note.mistake_type = payload.mistake_type
    note.manual_notes = payload.manual_notes
    note.tags = encode_tags(payload.tags)
    db.commit()
    db.refresh(round_row)
    return round_to_review(round_row)


def get_review_options(db: Session) -> schemas.ReviewOptionOut:
    notes = db.query(models.RoundNote).all()
    mistake_types = sorted({note.mistake_type for note in notes if note.mistake_type})
    tags = sorted({tag for note in notes for tag in decode_tags(note.tags)})
    return schemas.ReviewOptionOut(mistake_types=mistake_types, tags=tags)
