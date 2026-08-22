"""Reliable rule-based itinerary planner used directly or as an LLM fallback."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

from .budget_estimator import estimate_total
from .proposal_schema import PlannerProposal, ProposalItem


def _value(record: Any, name: str, default: Any = None) -> Any:
    if isinstance(record, Mapping):
        return record.get(name, default)
    return getattr(record, name, default)


def _request_value(request: Any, name: str, default: Any = None) -> Any:
    return _value(request, name, default) if request is not None else default


def _as_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _activity_score(activity: Any, preferences: Sequence[str], daily_budget: float | None) -> float:
    category = str(_value(activity, "category", "other") or "other").lower()
    searchable = " ".join(
        (category, str(_value(activity, "name", "")), str(_value(activity, "description", "")))
    ).lower()
    preference_score = sum(100 for preference in preferences if preference.lower() in searchable)
    cost = max(0.0, float(_value(activity, "cost", 0) or 0))
    duration = max(0.25, float(_value(activity, "duration_hours", 1) or 1))
    affordability = 0.0 if daily_budget is None else max(-30.0, 20.0 * (1 - cost / max(daily_budget, 1)))
    return preference_score + affordability - (cost * 0.02) - (duration * 0.01)


def rank_activities(
    activities: Sequence[Any],
    city_id: str,
    preferences: Sequence[str] | None = None,
    daily_budget: float | None = None,
) -> list[Any]:
    """Filter catalog activities to a city and rank them deterministically."""

    preferences = [str(value).strip().lower() for value in (preferences or []) if str(value).strip()]
    eligible = [item for item in activities if str(_value(item, "city_id", "")) == str(city_id)]
    return sorted(
        eligible,
        key=lambda item: (
            -_activity_score(item, preferences, daily_budget),
            float(_value(item, "cost", 0) or 0),
            str(_value(item, "name", "")).lower(),
            str(_value(item, "id", "")),
        ),
    )


def _time_slot(start_minutes: int) -> str:
    return f"{start_minutes // 60:02d}:{start_minutes % 60:02d}"


def build_rule_proposal(
    stops: Sequence[Any],
    activities: Sequence[Any],
    request: Any = None,
    *,
    goal: str = "balanced",
    preferences: Sequence[str] | None = None,
    daily_budget: float | None = None,
    notes: str | None = None,
) -> PlannerProposal:
    """Build a valid activity itinerary without external services.

    Request values take precedence over keyword defaults. Activities are never
    invented and are scheduled only within a stop whose city owns them.
    """

    goal = str(_request_value(request, "goal", goal) or "balanced").lower()
    preferences = list(_request_value(request, "preferences", preferences) or [])
    daily_budget_value = _request_value(request, "daily_budget", daily_budget)
    daily_budget = float(daily_budget_value) if daily_budget_value is not None else None
    notes = _request_value(request, "notes", notes)

    max_hours = 6.0 if goal == "relaxed" else 8.0
    max_items = 2 if goal == "relaxed" else (4 if goal == "packed" else 3)
    day_start = 10 * 60 if goal == "relaxed" or (notes and "morning" in str(notes).lower()) else 9 * 60
    items: list[ProposalItem] = []
    warnings: list[str] = []
    used_activity_ids: set[str] = set()

    ordered_stops = sorted(stops, key=lambda item: int(_value(item, "sequence", 10) or 10))
    for stop in ordered_stops:
        stop_id = str(_value(stop, "id", ""))
        city_id = str(_value(stop, "city_id", ""))
        start = _as_date(_value(stop, "start_date"))
        end = _as_date(_value(stop, "end_date"))
        if end < start:
            warnings.append(f"Stop {stop_id} has an invalid date range and was skipped.")
            continue

        candidates = rank_activities(activities, city_id, preferences, daily_budget)
        if not candidates:
            warnings.append(f"No catalog activities are available for stop {stop_id}.")
            continue

        for day_index in range(1, (end - start).days + 2):
            hours_used = 0.0
            cost_used = 0.0
            clock = day_start
            selected = 0
            for activity in candidates:
                activity_id = str(_value(activity, "id", ""))
                if not activity_id or activity_id in used_activity_ids:
                    continue
                duration = max(0.25, float(_value(activity, "duration_hours", 1) or 1))
                cost = max(0.0, float(_value(activity, "cost", 0) or 0))
                if duration > max_hours - hours_used:
                    continue
                if daily_budget is not None and cost > daily_budget - cost_used:
                    continue

                items.append(
                    ProposalItem(
                        stop_id=stop_id,
                        activity_id=activity_id,
                        name=str(_value(activity, "name", "Activity")),
                        day_index=day_index,
                        sequence=(selected + 1) * 10,
                        time_slot=_time_slot(clock),
                        cost=cost,
                        notes=f"Approximately {duration:g} hour{'s' if duration != 1 else ''}.",
                    )
                )
                used_activity_ids.add(activity_id)
                hours_used += duration
                cost_used += cost
                selected += 1
                clock += int(duration * 60) + 30
                if selected >= max_items:
                    break

    preference_text = ", ".join(str(value) for value in preferences) or "popular catalog"
    summary = f"A {goal} itinerary focused on {preference_text} activities."
    if not items:
        warnings.append("No activities matched the itinerary constraints.")
    return PlannerProposal(
        summary=summary,
        estimated_total=estimate_total(items),
        warnings=warnings,
        items=items,
    )
