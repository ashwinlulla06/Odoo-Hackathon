from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.city import City
from backend.schemas.city import CityOut

router = APIRouter(prefix="/api/cities", tags=["cities"])

@router.get("", response_model=list[CityOut])
def list_cities(db: Session = Depends(get_db)):
    return db.query(City).all()

@router.get("/{city_id}", response_model=CityOut)
def get_city(city_id: str, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city