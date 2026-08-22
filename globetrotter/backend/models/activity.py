import uuid
from sqlalchemy import Column, String, Float, Text, ForeignKey
from backend.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    city_id = Column(String, ForeignKey("cities.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, default="other")
    cost = Column(Float, default=0.0)
    duration_hours = Column(Float, default=1.0)
    description = Column(Text)
    image_url = Column(String)