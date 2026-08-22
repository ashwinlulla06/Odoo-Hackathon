"""Shared, backend-agnostic schemas for itinerary proposals."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProposalItem(BaseModel):
    """One activity proposed for a particular day of a trip stop."""

    # Gemini's response-schema API rejects JSON Schema's
    # ``additionalProperties`` keyword, which Pydantic emits for
    # ``extra='forbid'``. Unknown model fields may be ignored here because the
    # authoritative catalog/date/cost validator runs immediately afterward.
    model_config = ConfigDict(str_strip_whitespace=True)

    stop_id: str = Field(min_length=1)
    activity_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    day_index: int = Field(ge=1)
    sequence: int = Field(default=10, ge=0)
    time_slot: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    cost: float = Field(default=0.0, ge=0)
    notes: str | None = None

    @field_validator("cost")
    @classmethod
    def round_cost(cls, value: float) -> float:
        return round(value, 2)


class PlannerProposal(BaseModel):
    """Validated content produced by either Gemini or the rule planner."""

    model_config = ConfigDict(str_strip_whitespace=True)

    summary: str = Field(min_length=1)
    estimated_total: float = Field(default=0.0, ge=0)
    warnings: list[str] = Field(default_factory=list)
    items: list[ProposalItem] = Field(default_factory=list)

    @field_validator("estimated_total")
    @classmethod
    def round_total(cls, value: float) -> float:
        return round(value, 2)


PlannerGoal = Literal["balanced", "budget", "relaxed", "packed"]
