import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String, Text

from backend.database import Base


class TripExpense(Base):
    __tablename__ = "trip_expenses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False, index=True)
    stop_id = Column(String, ForeignKey("trip_stops.id"), nullable=True)
    category = Column(String, nullable=False, default="other")
    label = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    expense_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
