from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.trip import Trip
from backend.models.trip_stop import TripStop
from backend.models.itinerary_item import ItineraryItem

# This is the line your server was complaining was missing!
router = APIRouter(prefix="/api/public", tags=["public"])

@router.get("/trips/{share_token}")
def get_public_trip(share_token: str, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.share_token == share_token, Trip.is_public == True).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Public trip not found")
    
    # Fetch all nested data manually to return one massive payload
    stops = db.query(TripStop).filter(TripStop.trip_id == trip.id).order_by(TripStop.sequence).all()
    
    stops_with_items = []
    for stop in stops:
        items = db.query(ItineraryItem).filter(ItineraryItem.stop_id == stop.id).order_by(ItineraryItem.day_index, ItineraryItem.sequence).all()
        stop_dict = stop.__dict__.copy()
        stop_dict["items"] = items
        stops_with_items.append(stop_dict)
    
    return {
        "trip": trip,
        "stops": stops_with_items
    }