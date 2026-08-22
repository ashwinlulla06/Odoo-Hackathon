import uuid
from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stop_id = Column(String, ForeignKey("trip_stops.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=True)

    name = Column(String, nullable=False)
    day_index = Column(Integer, default=1)
    sequence = Column(Integer, default=10)
    time_slot = Column(String)
    cost = Column(Float, default=0.0)
    notes = Column(Text)

    stop = relationship("TripStop", back_populates="items")