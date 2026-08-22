import json
from pathlib import Path

from sqlalchemy.orm import Session

from backend.models.activity import Activity
from backend.models.city import City
from backend.models.itinerary_item import ItineraryItem
from backend.models.trip import Trip
from backend.models.trip_stop import TripStop

SEED_DIR = Path(__file__).resolve().parent / "seed_data"


def _records(filename: str, key: str) -> list[dict]:
    path = SEED_DIR / filename
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get(key, []) if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError(f"{filename} must contain a JSON list or a '{key}' list")
    return records


def seed_catalog(db: Session) -> None:
    """Synchronize the bundled India catalog without touching user-owned trips."""
    try:
        for trip in db.query(Trip).filter(Trip.owner_id == "demo-user").all():
            db.delete(trip)
        db.flush()

        city_records = _records("cities.json", "cities")
        city_ids = {row["id"] for row in city_records}
        for data in city_records:
            clean = {key: value for key, value in data.items()
                     if key in {"id", "name", "country", "cost_index", "popularity", "image_url"}}
            city = db.query(City).filter(City.id == clean["id"]).first()
            if city:
                for key, value in clean.items():
                    setattr(city, key, value)
            else:
                db.add(City(**clean))
        db.flush()

        cities_by_name = {city.name.lower(): city.id for city in db.query(City).all()}
        activity_records = _records("activities.json", "activities")
        activity_ids = {row["id"] for row in activity_records}
        for data in activity_records:
            clean = {key: value for key, value in data.items()
                     if key in {"id", "city_id", "name", "category", "cost", "duration_hours",
                                "description", "image_url"}}
            if not clean.get("city_id") and data.get("city"):
                clean["city_id"] = cities_by_name.get(str(data["city"]).lower())
            if not clean.get("city_id"):
                continue
            activity = db.query(Activity).filter(Activity.id == clean["id"]).first()
            if activity:
                for key, value in clean.items():
                    setattr(activity, key, value)
            else:
                db.add(Activity(**clean))
        db.flush()

        used_activity_ids = {row[0] for row in db.query(ItineraryItem.activity_id).filter(ItineraryItem.activity_id.isnot(None)).all()}
        for activity in db.query(Activity).filter(~Activity.id.in_(activity_ids)).all():
            if activity.id not in used_activity_ids:
                db.delete(activity)
        used_city_ids = {row[0] for row in db.query(TripStop.city_id).all()}
        for city in db.query(City).filter(~City.id.in_(city_ids)).all():
            if city.id not in used_city_ids:
                db.delete(city)
        db.commit()
    except Exception:
        db.rollback()
        raise
