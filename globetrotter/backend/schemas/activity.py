from typing import Optional
from pydantic import BaseModel, ConfigDict

class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    city_id: str
    name: str
    category: str
    cost: float
    duration_hours: float
    description: Optional[str] = None
    image_url: Optional[str] = None