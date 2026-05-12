from __future__ import annotations

from sqlalchemy.orm import Session

from .analytics import get_country_performance


def get_practice_priorities(db: Session) -> list[dict]:
    country_rows = get_country_performance(db)
    priorities: list[dict] = []

    for row in country_rows:
        if row.avg_score is None or row.correct_country_rate is None:
            continue
        weakness = max(0.0, 5000 - row.avg_score) / 5000
        uncertainty_boost = 1 / max(1, row.rounds_played) ** 0.5
        priority = 0.75 * weakness + 0.25 * (1 - row.correct_country_rate) + 0.15 * uncertainty_boost
        priorities.append(
            {
                "country": row.actual_country,
                "priority_score": round(priority, 4),
                "rounds_played": row.rounds_played,
                "avg_score": row.avg_score,
                "correct_country_rate": row.correct_country_rate,
            }
        )

    priorities.sort(key=lambda item: item["priority_score"], reverse=True)
    return priorities[:20]
