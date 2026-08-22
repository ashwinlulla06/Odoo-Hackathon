from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.activity import Activity
from backend.models.city import City
from backend.models.saved_city import SavedCity
from backend.models.user import User
from backend.schemas.activity import ActivityOut
from backend.schemas.city import CityOut

router = APIRouter(prefix="/api/v1", tags=["discovery"])


@router.get("/cities")
def list_cities(q: str | None = None, country: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(City).filter(City.country == "India")
    if q:
        query = query.filter(or_(City.name.ilike(f"%{q}%"), City.country.ilike(f"%{q}%")))
    if country:
        query = query.filter(City.country == country)
    total = query.count()
    items = query.order_by(City.popularity.desc(), City.name).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [CityOut.model_validate(item) for item in items], "total": total, "page": page, "page_size": page_size}


@router.get("/activities")
def list_activities(city_id: str | None = None, q: str | None = None, category: str | None = None, max_cost: float | None = Query(None, ge=0), max_duration: float | None = Query(None, ge=0), page: int = Query(1, ge=1), page_size: int = Query(48, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(Activity).join(City, Activity.city_id == City.id).filter(City.country == "India")
    if city_id:
        query = query.filter(Activity.city_id == city_id)
    if q:
        query = query.filter(or_(Activity.name.ilike(f"%{q}%"), Activity.description.ilike(f"%{q}%")))
    if category:
        query = query.filter(Activity.category == category)
    if max_cost is not None:
        query = query.filter(Activity.cost <= max_cost)
    if max_duration is not None:
        query = query.filter(Activity.duration_hours <= max_duration)
    total = query.count()
    items = query.order_by(Activity.cost, Activity.name).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [ActivityOut.model_validate(item) for item in items], "total": total, "page": page, "page_size": page_size}


@router.get("/me/saved-cities")
def saved_cities(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cities = db.query(City).join(SavedCity, SavedCity.city_id == City.id).filter(SavedCity.user_id == user.id).order_by(City.name).all()
    return [CityOut.model_validate(city) for city in cities]


@router.post("/me/saved-cities/{city_id}", status_code=status.HTTP_201_CREATED)
def save_city(city_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(City).filter(City.id == city_id).first():
        raise HTTPException(status_code=404, detail="City not found")
    existing = db.query(SavedCity).filter_by(user_id=user.id, city_id=city_id).first()
    if not existing:
        db.add(SavedCity(user_id=user.id, city_id=city_id))
        db.commit()
    return {"saved": True, "city_id": city_id}


@router.delete("/me/saved-cities/{city_id}")
def remove_saved_city(city_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(SavedCity).filter_by(user_id=user.id, city_id=city_id).first()
    if record:
        db.delete(record)
        db.commit()
    return {"saved": False, "city_id": city_id}
