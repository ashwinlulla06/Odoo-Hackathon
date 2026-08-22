from typing import Optional
from pydantic import BaseModel, ConfigDict

class ItineraryItemCreate(BaseModel):
    activity_id: Optional[str] = None
    name: str
    day_index: int
    sequence: int
    time_slot: Optional[str] = None
    cost: Optional[float] = 0.0
    notes: Optional[str] = None

class ItineraryItemUpdate(BaseModel):
    activity_id: Optional[str] = None
    name: Optional[str] = None
    day_index: Optional[int] = None
    sequence: Optional[int] = None
    time_slot: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

class ItineraryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    stop_id: str
    activity_id: Optional[str] = None
    name: str
    day_index: int
    sequence: int
    time_slot: Optional[str] = None
    cost: float
    notes: Optional[str] = None