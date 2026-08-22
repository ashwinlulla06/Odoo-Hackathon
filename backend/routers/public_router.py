import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.itinerary_item import ItineraryItem
from backend.models.trip import Trip
from backend.models.trip_stop import TripStop
from backend.models.user import User
from backend.routers.trip_v1_router import owned_trip, trip_dict

router = APIRouter(prefix="/api/v1", tags=["sharing"])


@router.post("/trips/{trip_id}/publish")
def publish_trip(trip_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user)
    trip.is_public = True
    if not trip.share_token:
        trip.share_token = secrets.token_urlsafe(10)
    db.commit(); db.refresh(trip)
    return {"is_public": True, "share_slug": trip.share_token, "public_url": f"/share/{trip.share_token}"}


@router.post("/trips/{trip_id}/unpublish")
def unpublish_trip(trip_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); trip.is_public = False; db.commit(); return {"is_public": False}


@router.get("/public/trips")
def public_trips(q: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(18, ge=1, le=50), db: Session = Depends(get_db)):
    query = db.query(Trip).filter(Trip.is_public.is_(True))
    if q: query = query.filter(Trip.name.ilike(f"%{q}%"))
    total = query.count(); rows = query.order_by(Trip.start_date.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"items":[trip_dict(db,row,nested=False) for row in rows],"total":total,"page":page,"page_size":page_size}


@router.get("/public/trips/{share_slug}")
def public_trip(share_slug: str, db: Session = Depends(get_db)):
    trip=db.query(Trip).filter(Trip.share_token==share_slug,Trip.is_public.is_(True)).first()
    if not trip: raise HTTPException(status_code=404,detail="Public itinerary not found")
    return trip_dict(db,trip)


@router.post("/public/trips/{share_slug}/copy",status_code=status.HTTP_201_CREATED)
def copy_public_trip(share_slug: str,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    source=db.query(Trip).filter(Trip.share_token==share_slug,Trip.is_public.is_(True)).first()
    if not source: raise HTTPException(status_code=404,detail="Public itinerary not found")
    clone=Trip(name=f"{source.name} - My copy",owner_id=user.id,start_date=source.start_date,end_date=source.end_date,description=source.description,cover_image_url=source.cover_image_url,budget_limit=source.budget_limit)
    db.add(clone); db.flush()
    for source_stop in sorted(source.stops,key=lambda row:row.sequence):
        stop=TripStop(trip_id=clone.id,city_id=source_stop.city_id,sequence=source_stop.sequence,start_date=source_stop.start_date,end_date=source_stop.end_date,description=source_stop.description)
        db.add(stop); db.flush()
        for source_item in source_stop.items:
            db.add(ItineraryItem(stop_id=stop.id,activity_id=source_item.activity_id,name=source_item.name,day_index=source_item.day_index,sequence=source_item.sequence,time_slot=source_item.time_slot,cost=source_item.cost,notes=source_item.notes))
    db.commit(); db.refresh(clone); return trip_dict(db,clone)
