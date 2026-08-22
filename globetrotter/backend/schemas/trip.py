from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TripCreate(BaseModel):
    name: str
    owner_id: str
    start_date: date
    end_date: date
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class TripUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_public: Optional[bool] = None


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    owner_id: str
    start_date: date
    end_date: date
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_public: bool
    share_token: Optional[str] = None
    total_budget: float