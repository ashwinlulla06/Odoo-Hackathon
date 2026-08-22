from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ProposalCreate(BaseModel):
    goal: Literal["balanced", "budget", "relaxed", "packed"] = "balanced"
    preferences: list[str] = Field(default_factory=list, max_length=20)
    daily_budget: float | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)
    use_llm: bool = True

    @field_validator("preferences")
    @classmethod
    def normalize_preferences(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value.strip().lower() for value in values if value.strip()))


class ProposalItemOut(BaseModel):
    stop_id: str
    activity_id: str
    name: str
    day_index: int = Field(ge=1)
    sequence: int = Field(ge=0)
    time_slot: str | None = None
    cost: float = Field(ge=0)
    notes: str | None = None


class ProposalOut(BaseModel):
    id: str
    trip_id: str
    status: Literal["ready", "applied", "failed"]
    source: Literal["gemini", "rules"]
    model: str | None = None
    summary: str
    estimated_total: float
    warnings: list[str] = Field(default_factory=list)
    items: list[ProposalItemOut] = Field(default_factory=list)
    created_at: datetime
    applied_at: datetime | None = None


class ProposalApplyOut(BaseModel):
    proposal_id: str
    trip_id: str
    status: Literal["applied"]
    created_item_ids: list[str]
    total_budget: float
