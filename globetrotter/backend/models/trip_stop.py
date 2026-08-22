import uuid
from sqlalchemy import Column, String, Date, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class TripStop(Base):
    __tablename__ = "trip_stops"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False)
    city_id = Column(String, ForeignKey("cities.id"), nullable=False)
    sequence = Column(Integer, default=10)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text)
    budget_estimate = Column(Float, default=0.0)

    trip = relationship("Trip", back_populates="stops")
    items = relationship(
        "ItineraryItem", back_populates="stop", cascade="all, delete-orphan"
    )