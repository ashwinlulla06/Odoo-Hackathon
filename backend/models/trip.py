import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, DateTime, Text, Boolean, Float
from sqlalchemy.orm import relationship
from backend.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    owner_id = Column(String, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text)
    cover_image_url = Column(String)

    is_public = Column(Boolean, default=False)
    share_token = Column(String, unique=True, nullable=True)

    total_budget = Column(Float, default=0.0)
    budget_limit = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    stops = relationship(
        "TripStop", back_populates="trip", cascade="all, delete-orphan",
        order_by="TripStop.sequence"
    )
    ai_proposals = relationship(
        "AIProposal", back_populates="trip", cascade="all, delete-orphan"
    )
    expenses = relationship("TripExpense", cascade="all, delete-orphan")
