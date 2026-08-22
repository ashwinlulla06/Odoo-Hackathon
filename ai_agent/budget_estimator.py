"""Deterministic activity-budget calculations."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any


def _value(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, Mapping):
        return item.get(name, default)
    return getattr(item, name, default)


def estimate_total(items: Iterable[Any]) -> float:
    """Return the activity-only total for proposal items."""

    return round(sum(max(0.0, float(_value(item, "cost", 0) or 0)) for item in items), 2)


def estimate_budget(items: Iterable[Any]) -> dict[str, Any]:
    """Return total plus stop/day subtotals for plain dict or object inputs."""

    materialized = list(items)
    by_stop: defaultdict[str, float] = defaultdict(float)
    by_day: defaultdict[str, float] = defaultdict(float)

    for item in materialized:
        stop_id = str(_value(item, "stop_id", ""))
        day_index = int(_value(item, "day_index", 1) or 1)
        cost = max(0.0, float(_value(item, "cost", 0) or 0))
        by_stop[stop_id] += cost
        by_day[f"{stop_id}:{day_index}"] += cost

    return {
        "total": estimate_total(materialized),
        "by_stop": {key: round(value, 2) for key, value in by_stop.items()},
        "by_day": {key: round(value, 2) for key, value in by_day.items()},
    }
