from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint

from backend.database import Base


class SavedCity(Base):
    __tablename__ = "saved_cities"
    __table_args__ = (UniqueConstraint("user_id", "city_id", name="uq_saved_city_user_city"),)

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    city_id = Column(String, ForeignKey("cities.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
