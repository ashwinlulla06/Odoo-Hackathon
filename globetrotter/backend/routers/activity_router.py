from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.activity import Activity
from backend.schemas.activity import ActivityOut

router = APIRouter(prefix="/api/activities", tags=["activities"])

@router.get("", response_model=list[ActivityOut])
def list_activities(city_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Activity)
    # If a city_id is passed, filter activities for just that city
    if city_id:
        query = query.filter(Activity.city_id == city_id)
    return query.all()

@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: str, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity