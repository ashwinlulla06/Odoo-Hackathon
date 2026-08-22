from typing import Optional
from pydantic import BaseModel, ConfigDict

class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country: str
    cost_index: int
    popularity: int
    image_url: Optional[str] = None