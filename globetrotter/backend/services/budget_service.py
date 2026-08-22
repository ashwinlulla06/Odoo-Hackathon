from sqlalchemy.orm import Session
from backend.models.trip import Trip
from backend.models.trip_stop import TripStop
from backend.models.itinerary_item import ItineraryItem

def calculate_trip_budget(trip_id: str, db: Session):
    stops = db.query(TripStop).filter(TripStop.trip_id == trip_id).all()
    
    total_stops_budget = 0.0
    total_items_budget = 0.0
    
    for stop in stops:
        total_stops_budget += (stop.budget_estimate or 0.0)
        
        items = db.query(ItineraryItem).filter(ItineraryItem.stop_id == stop.id).all()
        for item in items:
            total_items_budget += (item.cost or 0.0)
            
    total_budget = total_stops_budget + total_items_budget
    
    return {
        "trip_id": trip_id,
        "total_budget": total_budget,
        "breakdown": {
            "stops_estimates": total_stops_budget,
            "activities_cost": total_items_budget
        }
    }