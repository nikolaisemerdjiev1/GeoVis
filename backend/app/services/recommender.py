from __future__ import annotations

from collections import Counter
from datetime import datetime
from statistics import mean

from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from .round_review import decode_tags, round_to_review


MISS_SCORE_THRESHOLD = 4000


def _recency_weight(played_at: datetime, newest_played_at: datetime) -> float:
    age_days = max(0.0, (newest_played_at - played_at).total_seconds() / 86400)
    return 1 / (1 + age_days / 14)


def _is_country_miss(round_row: models.Round) -> bool:
    if round_row.score is not None and round_row.score < MISS_SCORE_THRESHOLD:
        return True
    return bool(
        round_row.actual_country
        and round_row.guessed_country
        and round_row.actual_country != round_row.guessed_country
    )


def _is_region_miss(round_row: models.Round) -> bool:
    if round_row.score is not None and round_row.score < MISS_SCORE_THRESHOLD:
        return True
    return bool(
        round_row.actual_region
        and round_row.guessed_region
        and (
            round_row.actual_country != round_row.guessed_country
            or round_row.actual_region != round_row.guessed_region
        )
    )


def _explain(
    *,
    avg_score: float | None,
    recent_misses: int,
    confusion_count: int,
    recency_weight: float,
) -> str:
    reasons: list[str] = []
    if avg_score is not None and avg_score < MISS_SCORE_THRESHOLD:
        reasons.append(f"low average score ({avg_score:.0f})")
    if recent_misses:
        reasons.append(f"{recent_misses} recent miss{'es' if recent_misses != 1 else ''}")
    if confusion_count:
        reasons.append(f"{confusion_count} recurring confusion{'s' if confusion_count != 1 else ''}")
    if recency_weight >= 0.75:
        reasons.append("seen recently")
    return "; ".join(reasons) or "limited data, worth sampling again"


def _recommendation(
    *,
    target_type: str,
    country: str | None,
    region: str | None,
    rows: list[models.Round],
    newest_played_at: datetime,
    confusion_count: int,
) -> schemas.PracticeRecommendationOut:
    scores = [row.score for row in rows if row.score is not None]
    avg_score = mean(scores) if scores else None
    recent_weights = [_recency_weight(row.game.played_at, newest_played_at) for row in rows]
    recency = mean(recent_weights) if recent_weights else 0.0
    miss_checker = _is_region_miss if target_type == "region" else _is_country_miss
    misses = [row for row in rows if miss_checker(row)]
    recent_misses = sum(1 for row in misses if _recency_weight(row.game.played_at, newest_played_at) >= 0.45)
    weakness = max(0.0, MISS_SCORE_THRESHOLD - (avg_score or MISS_SCORE_THRESHOLD)) / MISS_SCORE_THRESHOLD
    miss_rate = len(misses) / max(1, len(rows))
    confusion_rate = min(1.0, confusion_count / max(1, len(rows)))
    scarcity_boost = 1 / max(1, len(rows)) ** 0.5
    priority = 0.42 * weakness + 0.24 * miss_rate + 0.18 * confusion_rate + 0.11 * recency + 0.05 * scarcity_boost

    return schemas.PracticeRecommendationOut(
        target_type=target_type,
        country=country,
        region=region,
        priority_score=round(priority, 4),
        rounds_played=len(rows),
        avg_score=avg_score,
        recent_misses=recent_misses,
        confusion_count=confusion_count,
        recency_weight=round(recency, 4),
        explanation=_explain(
            avg_score=avg_score,
            recent_misses=recent_misses,
            confusion_count=confusion_count,
            recency_weight=recency,
        ),
    )


def get_practice_priorities(db: Session, limit: int = 20) -> list[schemas.PracticeRecommendationOut]:
    rows = (
        db.query(models.Round)
        .join(models.Game)
        .options(joinedload(models.Round.game))
        .order_by(models.Game.played_at.desc(), models.Round.round_number.asc())
        .all()
    )
    if not rows:
        return []

    newest_played_at = max(row.game.played_at for row in rows)
    country_groups: dict[str, list[models.Round]] = {}
    region_groups: dict[tuple[str, str], list[models.Round]] = {}
    country_confusions: Counter[str] = Counter()
    region_confusions: Counter[tuple[str, str]] = Counter()

    for row in rows:
        if row.actual_country:
            country_groups.setdefault(row.actual_country, []).append(row)
            if row.guessed_country and row.guessed_country != row.actual_country:
                country_confusions[row.actual_country] += 1
        if row.actual_country and row.actual_region:
            region_key = (row.actual_country, row.actual_region)
            region_groups.setdefault(region_key, []).append(row)
            if (
                row.guessed_region
                and (row.guessed_country != row.actual_country or row.guessed_region != row.actual_region)
            ):
                region_confusions[region_key] += 1

    priorities: list[schemas.PracticeRecommendationOut] = []
    for country, grouped_rows in country_groups.items():
        priorities.append(
            _recommendation(
                target_type="country",
                country=country,
                region=None,
                rows=grouped_rows,
                newest_played_at=newest_played_at,
                confusion_count=country_confusions[country],
            )
        )

    for (country, region), grouped_rows in region_groups.items():
        priorities.append(
            _recommendation(
                target_type="region",
                country=country,
                region=region,
                rows=grouped_rows,
                newest_played_at=newest_played_at,
                confusion_count=region_confusions[(country, region)],
            )
        )

    priorities.sort(key=lambda item: item.priority_score, reverse=True)
    return priorities[:limit]


def get_review_queue(db: Session, limit: int = 12) -> schemas.ReviewQueueOut:
    rows = (
        db.query(models.Round)
        .join(models.Game)
        .options(joinedload(models.Round.game), joinedload(models.Round.note))
        .order_by(models.Game.played_at.desc(), models.Round.round_number.asc())
        .all()
    )

    recent_misses = [round_to_review(row) for row in rows if _is_country_miss(row) or _is_region_miss(row)]

    confusion_pairs = Counter(
        (
            row.actual_country,
            row.actual_region,
            row.guessed_country,
            row.guessed_region,
        )
        for row in rows
        if (row.actual_country, row.actual_region) != (row.guessed_country, row.guessed_region)
        and (row.guessed_country or row.guessed_region)
    )
    recurring_keys = {key for key, count in confusion_pairs.items() if count > 1}
    recurring_confusions = [
        round_to_review(row)
        for row in rows
        if (
            row.actual_country,
            row.actual_region,
            row.guessed_country,
            row.guessed_region,
        )
        in recurring_keys
    ]

    tagged_rounds = [round_to_review(row) for row in rows if row.note and decode_tags(row.note.tags)]

    return schemas.ReviewQueueOut(
        recent_misses=recent_misses[:limit],
        recurring_confusions=recurring_confusions[:limit],
        tagged_rounds=tagged_rounds[:limit],
    )
