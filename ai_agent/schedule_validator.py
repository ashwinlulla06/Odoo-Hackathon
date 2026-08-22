"""Authoritative validation for rule-based and LLM-generated proposals."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

from .budget_estimator import estimate_total
from .proposal_schema import PlannerProposal


class ProposalValidationError(ValueError):
    """Raised when a proposal is unsafe to persist or apply."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _value(record: Any, name: str, default: Any = None) -> Any:
    if isinstance(record, Mapping):
        return record.get(name, default)
    return getattr(record, name, default)


def _as_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def validate_proposal(
    proposal: PlannerProposal | Mapping[str, Any],
    stops: Sequence[Any],
    activities: Sequence[Any],
    max_daily_hours: float = 8.0,
) -> list[str]:
    """Return all proposal errors; an empty list means the proposal is valid."""

    try:
        parsed = proposal if isinstance(proposal, PlannerProposal) else PlannerProposal.model_validate(proposal)
    except Exception as exc:
        return [f"Proposal schema is invalid: {exc}"]

    stop_map = {str(_value(stop, "id", "")): stop for stop in stops}
    activity_map = {str(_value(activity, "id", "")): activity for activity in activities}
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    daily_hours: defaultdict[tuple[str, int], float] = defaultdict(float)
    daily_intervals: defaultdict[tuple[str, int], list[tuple[int, int, int]]] = defaultdict(list)

    for index, item in enumerate(parsed.items, start=1):
        prefix = f"Item {index}"
        stop = stop_map.get(item.stop_id)
        activity = activity_map.get(item.activity_id)
        if stop is None:
            errors.append(f"{prefix} references unknown stop {item.stop_id}.")
            continue
        if activity is None:
            errors.append(f"{prefix} references unknown activity {item.activity_id}.")
            continue
        if str(_value(activity, "city_id", "")) != str(_value(stop, "city_id", "")):
            errors.append(f"{prefix} activity does not belong to the stop city.")

        start = _as_date(_value(stop, "start_date"))
        end = _as_date(_value(stop, "end_date"))
        day_count = (end - start).days + 1
        if day_count < 1 or item.day_index > day_count:
            errors.append(f"{prefix} day_index is outside the stop date range.")

        duplicate_key = (item.stop_id, item.activity_id)
        if duplicate_key in seen:
            errors.append(f"{prefix} duplicates an activity in the same stop.")
        seen.add(duplicate_key)

        catalog_cost = round(max(0.0, float(_value(activity, "cost", 0) or 0)), 2)
        if abs(item.cost - catalog_cost) > 0.01:
            errors.append(f"{prefix} cost does not match the activity catalog.")
        duration = max(0.0, float(_value(activity, "duration_hours", 1) or 1))
        daily_hours[(item.stop_id, item.day_index)] += duration
        hour, minute = (int(value) for value in item.time_slot.split(":"))
        start_minutes = hour * 60 + minute
        end_minutes = start_minutes + round(duration * 60)
        intervals = daily_intervals[(item.stop_id, item.day_index)]
        for other_start, other_end, other_index in intervals:
            if start_minutes < other_end and other_start < end_minutes:
                errors.append(f"{prefix} overlaps item {other_index} on the same day.")
        intervals.append((start_minutes, end_minutes, index))

    for (stop_id, day_index), hours in daily_hours.items():
        if hours > max_daily_hours + 1e-9:
            errors.append(f"Stop {stop_id} day {day_index} exceeds {max_daily_hours:g} scheduled hours.")

    expected_total = estimate_total(parsed.items)
    if abs(parsed.estimated_total - expected_total) > 0.01:
        errors.append("estimated_total does not match the proposal item costs.")
    return errors


def validate_or_raise(
    proposal: PlannerProposal | Mapping[str, Any],
    stops: Sequence[Any],
    activities: Sequence[Any],
    max_daily_hours: float = 8.0,
) -> None:
    errors = validate_proposal(proposal, stops, activities, max_daily_hours)
    if errors:
        raise ProposalValidationError(errors)
