from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SignupIn(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(default="", max_length=80)
    phone: str | None = Field(default=None, max_length=40)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address")
        return value


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    city: str | None = None
    country: str | None = None
    avatar_url: str | None = None
    language: str
    is_active: bool
    is_admin: bool
    created_at: datetime


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=40)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = None
    language: str | None = Field(default=None, max_length=40)


class AuthOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserOut


class TripCreateV1(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    start_date: date
    end_date: date
    description: str | None = Field(default=None, max_length=2000)
    cover_image_url: str | None = None
    budget_limit: float | None = Field(default=None, ge=0)

    @field_validator("end_date")
    @classmethod
    def valid_dates(cls, value: date, info):
        start = info.data.get("start_date")
        if start and value < start:
            raise ValueError("End date must be on or after start date")
        return value


class TripUpdateV1(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = Field(default=None, max_length=2000)
    cover_image_url: str | None = None
    budget_limit: float | None = Field(default=None, ge=0)


class StopCreate(BaseModel):
    city_id: str
    start_date: date
    end_date: date
    description: str | None = None


class StopUpdate(BaseModel):
    city_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class ItemCreate(BaseModel):
    activity_id: str | None = None
    name: str | None = None
    day_index: int = Field(default=1, ge=1)
    time_slot: str | None = None
    cost: float | None = Field(default=None, ge=0)
    notes: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    day_index: int | None = Field(default=None, ge=1)
    time_slot: str | None = None
    cost: float | None = Field(default=None, ge=0)
    notes: str | None = None


class ReorderIn(BaseModel):
    ordered_ids: list[str] = Field(min_length=1)


class ExpenseCreate(BaseModel):
    category: Literal["transport", "stay", "meals", "other"]
    label: str = Field(min_length=1, max_length=160)
    amount: float = Field(ge=0)
    expense_date: date | None = None
    stop_id: str | None = None
    notes: str | None = None


class ExpenseUpdate(BaseModel):
    category: Literal["transport", "stay", "meals", "other"] | None = None
    label: str | None = Field(default=None, min_length=1, max_length=160)
    amount: float | None = Field(default=None, ge=0)
    expense_date: date | None = None
    stop_id: str | None = None
    notes: str | None = None


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    is_admin: bool | None = None
