import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class AIProposal(Base):
    __tablename__ = "ai_proposals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="ready")
    source = Column(String, nullable=False, default="rules")
    model = Column(String, nullable=True)
    request_data = Column(JSON, nullable=False, default=dict)
    proposal_data = Column(JSON, nullable=False, default=dict)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    applied_at = Column(DateTime(timezone=True), nullable=True)

    trip = relationship("Trip", back_populates="ai_proposals")
