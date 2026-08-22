import uuid
from sqlalchemy import Column, String, Float, Integer
from backend.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    cost_index = Column(Float, default=1.0)
    popularity = Column(Integer, default=0)
    image_url = Column(String)