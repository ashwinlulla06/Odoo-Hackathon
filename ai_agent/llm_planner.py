"""Optional Gemini enhancement for the GlobeTrotter planner."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .budget_estimator import estimate_total
from .proposal_schema import PlannerProposal
from .schedule_validator import validate_or_raise


DEFAULT_MODEL = "gemini-3.5-flash-lite"


class PlannerUnavailableError(RuntimeError):
    """Controlled error indicating that the caller should use rule fallback."""


def _value(record: Any, name: str, default: Any = None) -> Any:
    if isinstance(record, Mapping):
        return record.get(name, default)
    return getattr(record, name, default)


def _request_value(request: Any, name: str, default: Any = None) -> Any:
    return _value(request, name, default) if request is not None else default


def _serializable_records(records: Sequence[Any], fields: Sequence[str]) -> list[dict[str, Any]]:
    result = []
    for record in records:
        row = {field: _value(record, field) for field in fields}
        result.append({key: value.isoformat() if hasattr(value, "isoformat") else value for key, value in row.items()})
    return result


def generate_llm_proposal(
    stops: Sequence[Any],
    activities: Sequence[Any],
    request: Any = None,
    *,
    goal: str = "balanced",
    preferences: Sequence[str] | None = None,
    daily_budget: float | None = None,
    notes: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    timeout_seconds: float = 25.0,
) -> PlannerProposal:
    """Generate and validate a proposal with Gemini.

    No backend models are imported, and no database writes occur. Every failure
    becomes ``PlannerUnavailableError`` so the service can safely fall back.
    """

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise PlannerUnavailableError("GEMINI_API_KEY is not configured")
    if os.getenv("AI_ENABLED", "true").strip().lower() in {"0", "false", "no", "off"}:
        raise PlannerUnavailableError("AI generation is disabled")

    goal = str(_request_value(request, "goal", goal) or "balanced")
    preferences = list(_request_value(request, "preferences", preferences) or [])
    daily_budget = _request_value(request, "daily_budget", daily_budget)
    notes = _request_value(request, "notes", notes)

    stop_rows = _serializable_records(
        stops, ("id", "city_id", "start_date", "end_date", "sequence", "description")
    )
    activity_rows = _serializable_records(
        activities, ("id", "city_id", "name", "category", "cost", "duration_hours", "description")
    )
    prompt_template = (Path(__file__).parent / "prompts" / "planner_prompt.txt").read_text(encoding="utf-8")
    payload = {
        "goal": goal,
        "preferences": preferences,
        "daily_budget": daily_budget,
        "notes": notes,
        "stops": stop_rows,
        "approved_activities": activity_rows,
    }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=key,
            http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
        )
        response = client.models.generate_content(
            model=model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
            contents=f"{prompt_template}\n\nINPUT JSON:\n{json.dumps(payload, ensure_ascii=False)}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PlannerProposal,
                temperature=0.3,
            ),
        )
        if getattr(response, "parsed", None) is not None:
            parsed = PlannerProposal.model_validate(response.parsed)
        elif getattr(response, "text", None):
            parsed = PlannerProposal.model_validate_json(response.text)
        else:
            raise ValueError("Gemini returned an empty response")

        # Treat the catalog as authoritative even if the model copies costs incorrectly.
        parsed = parsed.model_copy(update={"estimated_total": estimate_total(parsed.items)})
        validate_or_raise(parsed, stops, activities)
        return parsed
    except PlannerUnavailableError:
        raise
    except Exception as exc:
        raise PlannerUnavailableError(f"Gemini planner unavailable: {exc}") from exc
