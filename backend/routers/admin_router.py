from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.auth import get_admin_user
from backend.database import get_db
from backend.models.activity import Activity
from backend.models.ai_proposal import AIProposal
from backend.models.city import City
from backend.models.itinerary_item import ItineraryItem
from backend.models.trip import Trip
from backend.models.trip_stop import TripStop
from backend.models.user import User
from backend.schemas.app import AdminUserUpdate, UserOut

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/analytics")
def analytics(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    city_rows = db.query(City.name).join(TripStop, TripStop.city_id == City.id).all()
    activity_rows = db.query(Activity.name).join(ItineraryItem, ItineraryItem.activity_id == Activity.id).all()
    source_rows = db.query(AIProposal.source).all()
    return {
        "totals": {"users": db.query(User).count(), "trips": db.query(Trip).count(), "public_trips": db.query(Trip).filter(Trip.is_public.is_(True)).count(), "cities": db.query(City).count(), "activities": db.query(Activity).count(), "ai_proposals": db.query(AIProposal).count()},
        "popular_cities": [{"name": name, "count": count} for name, count in Counter(row[0] for row in city_rows).most_common(5)],
        "popular_activities": [{"name": name, "count": count} for name, count in Counter(row[0] for row in activity_rows).most_common(5)],
        "ai_sources": dict(Counter(row[0] for row in source_rows)),
    }


@router.get("/users")
def users(q: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=100), _: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    query = db.query(User)
    if q: query = query.filter(User.email.ilike(f"%{q}%"))
    total=query.count(); rows=query.order_by(User.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"items":[UserOut.model_validate(row) for row in rows],"total":total,"page":page,"page_size":page_size}


@router.patch("/users/{user_id}",response_model=UserOut)
def update_user(user_id: str,payload: AdminUserUpdate,admin: User=Depends(get_admin_user),db: Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user_id).first()
    if not user: raise HTTPException(status_code=404,detail="User not found")
    values=payload.model_dump(exclude_unset=True)
    if user.id==admin.id and values.get("is_active") is False: raise HTTPException(status_code=422,detail="You cannot disable your own account")
    for key,value in values.items(): setattr(user,key,value)
    db.commit(); db.refresh(user); return user
