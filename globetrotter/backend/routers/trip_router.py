from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.trip import Trip
from backend.schemas.trip import TripCreate, TripUpdate, TripOut

from backend.models.trip_stop import TripStop
from backend.schemas.trip_stop import TripStopCreate, TripStopUpdate, TripStopOut

from backend.models.itinerary_item import ItineraryItem
from backend.schemas.itinerary_item import ItineraryItemCreate, ItineraryItemUpdate, ItineraryItemOut

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.post("", response_model=TripOut)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)):
    trip = Trip(**payload.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("", response_model=list[TripOut])
def list_trips(owner_id: str, db: Session = Depends(get_db)):
    return db.query(Trip).filter(Trip.owner_id == owner_id).all()


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: str, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.patch("/{trip_id}", response_model=TripOut)
def update_trip(trip_id: str, payload: TripUpdate, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}")
def delete_trip(trip_id: str, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"deleted": True}

@router.post("/{trip_id}/stops", response_model=TripStopOut)
def create_trip_stop(trip_id: str, payload: TripStopCreate, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip_stop = TripStop(trip_id=trip_id, **payload.model_dump())
    db.add(trip_stop)
    db.commit()
    db.refresh(trip_stop)
    return trip_stop

@router.get("/{trip_id}/stops", response_model=list[TripStopOut])
def list_trip_stops(trip_id: str, db: Session = Depends(get_db)):
    return db.query(TripStop).filter(TripStop.trip_id == trip_id).order_by(TripStop.sequence).all()

@router.patch("/{trip_id}/stops/{stop_id}", response_model=TripStopOut)
def update_trip_stop(trip_id: str, stop_id: str, payload: TripStopUpdate, db: Session = Depends(get_db)):
    stop = db.query(TripStop).filter(TripStop.id == stop_id, TripStop.trip_id == trip_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Trip stop not found")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(stop, field, value)
    db.commit()
    db.refresh(stop)
    return stop

@router.delete("/{trip_id}/stops/{stop_id}")
def delete_trip_stop(trip_id: str, stop_id: str, db: Session = Depends(get_db)):
    stop = db.query(TripStop).filter(TripStop.id == stop_id, TripStop.trip_id == trip_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Trip stop not found")
    db.delete(stop)
    db.commit()
    return {"deleted": True}

@router.post("/{trip_id}/stops/{stop_id}/items", response_model=ItineraryItemOut)
def create_itinerary_item(trip_id: str, stop_id: str, payload: ItineraryItemCreate, db: Session = Depends(get_db)):
    # Verify the stop exists and actually belongs to this trip
    stop = db.query(TripStop).filter(TripStop.id == stop_id, TripStop.trip_id == trip_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Trip stop not found")
    
    item = ItineraryItem(stop_id=stop_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{trip_id}/stops/{stop_id}/items", response_model=list[ItineraryItemOut])
def list_itinerary_items(trip_id: str, stop_id: str, db: Session = Depends(get_db)):
    return db.query(ItineraryItem).filter(ItineraryItem.stop_id == stop_id).order_by(ItineraryItem.day_index, ItineraryItem.sequence).all()

@router.patch("/{trip_id}/stops/{stop_id}/items/{item_id}", response_model=ItineraryItemOut)
def update_itinerary_item(trip_id: str, stop_id: str, item_id: str, payload: ItineraryItemUpdate, db: Session = Depends(get_db)):
    item = db.query(ItineraryItem).filter(ItineraryItem.id == item_id, ItineraryItem.stop_id == stop_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{trip_id}/stops/{stop_id}/items/{item_id}")
def delete_itinerary_item(trip_id: str, stop_id: str, item_id: str, db: Session = Depends(get_db)):
    item = db.query(ItineraryItem).filter(ItineraryItem.id == item_id, ItineraryItem.stop_id == stop_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}