from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TripStopCreate(BaseModel):
    city_id: str
    sequence: int
    start_date: date
    end_date: date
    description: Optional[str] = None
    budget_estimate: Optional[float] = 0.0

class TripStopUpdate(BaseModel):
    city_id: Optional[str] = None
    sequence: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    budget_estimate: Optional[float] = None

class TripStopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    city_id: str
    sequence: int
    start_date: date
    end_date: date
    description: Optional[str] = None
    budget_estimate: float