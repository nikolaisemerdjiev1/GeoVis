from __future__ import annotations

from statistics import median

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from .. import models, schemas


def get_recent_games(db: Session, limit: int = 20) -> list[models.Game]:
    return (
        db.query(models.Game)
        .order_by(desc(models.Game.played_at))
        .limit(limit)
        .all()
    )


def get_country_performance(db: Session) -> list[schemas.CountryPerformanceOut]:
    rounds = (
        db.query(models.Round)
        .filter(models.Round.actual_country.is_not(None))
        .all()
    )

    grouped: dict[str, list[models.Round]] = {}
    for row in rounds:
        key = row.actual_country or "Unknown"
        grouped.setdefault(key, []).append(row)

    output: list[schemas.CountryPerformanceOut] = []
    for country, items in grouped.items():
        scores = [item.score for item in items if item.score is not None]
        distances = [item.distance_km for item in items if item.distance_km is not None]
        correct = [
            item
            for item in items
            if item.guessed_country and item.actual_country and item.guessed_country == item.actual_country
        ]
        output.append(
            schemas.CountryPerformanceOut(
                actual_country=country,
                rounds_played=len(items),
                avg_score=(sum(scores) / len(scores)) if scores else None,
                median_distance_km=median(distances) if distances else None,
                avg_distance_km=(sum(distances) / len(distances)) if distances else None,
                correct_country_rate=(len(correct) / len(items)) if items else None,
            )
        )

    output.sort(key=lambda row: (row.rounds_played, row.avg_score or 0), reverse=True)
    return output


def get_region_performance(db: Session) -> list[schemas.RegionPerformanceOut]:
    rounds = (
        db.query(models.Round)
        .filter(models.Round.actual_country.is_not(None))
        .filter(models.Round.actual_region.is_not(None))
        .all()
    )

    grouped: dict[tuple[str, str], list[models.Round]] = {}
    for row in rounds:
        key = (row.actual_country or "Unknown", row.actual_region or "Unknown")
        grouped.setdefault(key, []).append(row)

    output: list[schemas.RegionPerformanceOut] = []
    for (country, region), items in grouped.items():
        scores = [item.score for item in items if item.score is not None]
        distances = [item.distance_km for item in items if item.distance_km is not None]
        correct = [
            item
            for item in items
            if item.guessed_country
            and item.guessed_region
            and item.actual_country == item.guessed_country
            and item.actual_region == item.guessed_region
        ]
        output.append(
            schemas.RegionPerformanceOut(
                country=country,
                region=region,
                rounds_played=len(items),
                avg_score=(sum(scores) / len(scores)) if scores else None,
                median_distance_km=median(distances) if distances else None,
                avg_distance_km=(sum(distances) / len(distances)) if distances else None,
                correct_region_rate=(len(correct) / len(items)) if items else None,
            )
        )

    output.sort(key=lambda row: (row.rounds_played, row.avg_score or 0), reverse=True)
    return output


def get_confusion_matrix(db: Session, limit: int = 100) -> list[schemas.ConfusionEntryOut]:
    rows = (
        db.query(
            models.Round.actual_country,
            models.Round.guessed_country,
            func.count(models.Round.id).label("count"),
        )
        .filter(models.Round.actual_country.is_not(None))
        .filter(models.Round.guessed_country.is_not(None))
        .group_by(models.Round.actual_country, models.Round.guessed_country)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [
        schemas.ConfusionEntryOut(
            actual_country=row.actual_country,
            guessed_country=row.guessed_country,
            count=row.count,
        )
        for row in rows
    ]


def get_region_confusion_matrix(db: Session, limit: int = 100) -> list[schemas.RegionConfusionEntryOut]:
    rows = (
        db.query(
            models.Round.actual_country,
            models.Round.actual_region,
            models.Round.guessed_country,
            models.Round.guessed_region,
            func.count(models.Round.id).label("count"),
        )
        .filter(models.Round.actual_country.is_not(None))
        .filter(models.Round.actual_region.is_not(None))
        .filter(models.Round.guessed_region.is_not(None))
        .group_by(
            models.Round.actual_country,
            models.Round.actual_region,
            models.Round.guessed_country,
            models.Round.guessed_region,
        )
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [
        schemas.RegionConfusionEntryOut(
            actual_country=row.actual_country,
            actual_region=row.actual_region,
            guessed_country=row.guessed_country,
            guessed_region=row.guessed_region,
            count=row.count,
        )
        for row in rows
    ]


def get_score_trend(db: Session, limit: int = 100) -> list[schemas.ScoreTrendEntryOut]:
    rows = (
        db.query(models.Game)
        .order_by(models.Game.played_at.asc())
        .limit(limit)
        .all()
    )
    return [
        schemas.ScoreTrendEntryOut(
            played_at=row.played_at,
            total_score=row.total_score,
            map_name=row.map_name,
            mode=row.mode,
        )
        for row in rows
    ]
