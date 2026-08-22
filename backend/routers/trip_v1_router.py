import secrets
from collections import defaultdict
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.activity import Activity
from backend.models.city import City
from backend.models.itinerary_item import ItineraryItem
from backend.models.trip import Trip
from backend.models.trip_expense import TripExpense
from backend.models.trip_stop import TripStop
from backend.models.user import User
from backend.schemas.app import ExpenseCreate, ExpenseUpdate, ItemCreate, ItemUpdate, ReorderIn, StopCreate, StopUpdate, TripCreateV1, TripUpdateV1

router = APIRouter(prefix="/api/v1/trips", tags=["trips v1"])


def owned_trip(db: Session, trip_id: str, user: User) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id == user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def item_dict(item: ItineraryItem, activity: Activity | None = None) -> dict:
    return {"id": item.id, "stop_id": item.stop_id, "activity_id": item.activity_id, "name": item.name,
            "day_index": item.day_index, "sequence": item.sequence, "time_slot": item.time_slot,
            "cost": float(item.cost or 0), "notes": item.notes,
            "category": activity.category if activity else "other", "duration_hours": float(activity.duration_hours or 0) if activity else None,
            "image_url": activity.image_url if activity else None}


def stop_dict(db: Session, stop: TripStop) -> dict:
    city = db.query(City).filter(City.id == stop.city_id).first()
    activity_ids = {item.activity_id for item in stop.items if item.activity_id}
    activities = {row.id: row for row in db.query(Activity).filter(Activity.id.in_(activity_ids)).all()} if activity_ids else {}
    return {"id": stop.id, "trip_id": stop.trip_id, "city_id": stop.city_id, "sequence": stop.sequence,
            "start_date": stop.start_date, "end_date": stop.end_date, "description": stop.description,
            "budget_estimate": float(stop.budget_estimate or 0),
            "city": {"id": city.id, "name": city.name, "country": city.country, "cost_index": city.cost_index, "image_url": city.image_url} if city else None,
            "items": [item_dict(item, activities.get(item.activity_id)) for item in sorted(stop.items, key=lambda row: (row.day_index, row.sequence))]}


def trip_dict(db: Session, trip: Trip, nested: bool = True) -> dict:
    stops = sorted(trip.stops, key=lambda row: (row.start_date, row.sequence)) if nested else []
    return {"id": trip.id, "name": trip.name, "owner_id": trip.owner_id, "start_date": trip.start_date,
            "end_date": trip.end_date, "description": trip.description, "cover_image_url": trip.cover_image_url,
            "is_public": bool(trip.is_public), "share_token": trip.share_token,
            "total_budget": float(trip.total_budget or 0), "budget_limit": trip.budget_limit,
            "created_at": trip.created_at, "updated_at": trip.updated_at,
            "destination_count": len(trip.stops), "stops": [stop_dict(db, stop) for stop in stops]}


def validate_stop_dates(trip: Trip, start_date, end_date) -> None:
    if end_date < start_date:
        raise HTTPException(status_code=422, detail="Stop end date must be on or after its start date")
    if start_date < trip.start_date or end_date > trip.end_date:
        raise HTTPException(status_code=422, detail="Stop dates must fall within the trip dates")


def validate_stop_destination(db: Session, trip: Trip, city_id: str, start_date, end_date, exclude_stop_id: str | None = None) -> City:
    city = db.query(City).filter(City.id == city_id, City.country == "India").first()
    if not city:
        raise HTTPException(status_code=404, detail="Choose a valid Indian destination")
    for other in trip.stops:
        if other.id == exclude_stop_id:
            continue
        if other.city_id == city_id:
            raise HTTPException(status_code=409, detail=f"{city.name} is already included in this trip")
        if start_date <= other.end_date and other.start_date <= end_date:
            raise HTTPException(status_code=409, detail="Destination dates overlap another stop")
    return city


def _minutes(time_slot: str) -> int:
    hour, minute = (int(value) for value in time_slot.split(":"))
    return hour * 60 + minute


def _available_time(db: Session, stop: TripStop, day_index: int, duration_hours: float, requested: str | None = None, exclude_item_id: str | None = None) -> str:
    occupied = []
    for row in stop.items:
        if row.id == exclude_item_id or row.day_index != day_index or not row.time_slot:
            continue
        activity = db.query(Activity).filter(Activity.id == row.activity_id).first()
        start = _minutes(row.time_slot)
        occupied.append((start, start + round(float(activity.duration_hours or 1) * 60) if activity else start + 60))
    duration = round(max(duration_hours, 0.25) * 60)
    candidates = [_minutes(requested)] if requested else list(range(9 * 60, 20 * 60 + 1, 30))
    for start in candidates:
        end = start + duration
        if end <= 22 * 60 and all(not (start < used_end and used_start < end) for used_start, used_end in occupied):
            return f"{start // 60:02d}:{start % 60:02d}"
    if requested:
        raise HTTPException(status_code=409, detail=f"{requested} clashes with another activity on day {day_index}")
    raise HTTPException(status_code=409, detail=f"No free time remains on day {day_index}")


def recalculate_budget(db: Session, trip: Trip) -> float:
    db.flush()
    activity_total = db.query(ItineraryItem).join(TripStop).filter(TripStop.trip_id == trip.id).all()
    manual_total = db.query(TripExpense).filter(TripExpense.trip_id == trip.id).all()
    for stop in db.query(TripStop).filter(TripStop.trip_id == trip.id).all():
        stop_items = db.query(ItineraryItem).filter(ItineraryItem.stop_id == stop.id).all()
        stop.budget_estimate = round(sum(float(item.cost or 0) for item in stop_items), 2)
    trip.total_budget = round(sum(float(item.cost or 0) for item in activity_total) + sum(float(expense.amount or 0) for expense in manual_total), 2)
    return trip.total_budget


@router.get("")
def list_trips(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Trip).filter(Trip.owner_id == user.id).order_by(Trip.start_date.desc()).all()
    return [trip_dict(db, trip, nested=False) for trip in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripCreateV1, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = Trip(owner_id=user.id, **payload.model_dump())
    db.add(trip); db.commit(); db.refresh(trip)
    return trip_dict(db, trip)


@router.get("/{trip_id}")
def get_trip(trip_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return trip_dict(db, owned_trip(db, trip_id, user))


@router.patch("/{trip_id}")
def update_trip(trip_id: str, payload: TripUpdateV1, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user)
    values = payload.model_dump(exclude_unset=True)
    start, end = values.get("start_date", trip.start_date), values.get("end_date", trip.end_date)
    if end < start:
        raise HTTPException(status_code=422, detail="Trip end date must be on or after its start date")
    for key, value in values.items(): setattr(trip, key, value)
    db.commit(); db.refresh(trip)
    return trip_dict(db, trip)


@router.delete("/{trip_id}")
def delete_trip(trip_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); db.delete(trip); db.commit(); return {"deleted": True}


@router.post("/{trip_id}/stops", status_code=status.HTTP_201_CREATED)
def add_stop(trip_id: str, payload: StopCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); validate_stop_dates(trip, payload.start_date, payload.end_date)
    validate_stop_destination(db, trip, payload.city_id, payload.start_date, payload.end_date)
    sequence = (max((stop.sequence for stop in trip.stops), default=0) // 10 + 1) * 10
    stop = TripStop(trip_id=trip.id, sequence=sequence, **payload.model_dump()); db.add(stop); db.commit(); db.refresh(stop)
    return stop_dict(db, stop)


@router.patch("/{trip_id}/stops/{stop_id}")
def update_stop(trip_id: str, stop_id: str, payload: StopUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); stop = db.query(TripStop).filter_by(id=stop_id, trip_id=trip.id).first()
    if not stop: raise HTTPException(status_code=404, detail="Stop not found")
    values = payload.model_dump(exclude_unset=True); start, end = values.get("start_date", stop.start_date), values.get("end_date", stop.end_date); validate_stop_dates(trip, start, end)
    validate_stop_destination(db, trip, values.get("city_id", stop.city_id), start, end, stop.id)
    for key, value in values.items(): setattr(stop, key, value)
    db.commit(); db.refresh(stop); return stop_dict(db, stop)


@router.delete("/{trip_id}/stops/{stop_id}")
def delete_stop(trip_id: str, stop_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); stop = db.query(TripStop).filter_by(id=stop_id, trip_id=trip.id).first()
    if not stop: raise HTTPException(status_code=404, detail="Stop not found")
    db.delete(stop); recalculate_budget(db, trip); db.commit(); return {"deleted": True}


@router.post("/{trip_id}/stops/reorder")
def reorder_stops(trip_id: str, payload: ReorderIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); rows = {row.id: row for row in trip.stops}
    if set(payload.ordered_ids) != set(rows): raise HTTPException(status_code=422, detail="ordered_ids must contain every stop exactly once")
    for index, row_id in enumerate(payload.ordered_ids, 1): rows[row_id].sequence = index * 10
    db.commit(); return trip_dict(db, trip)


@router.post("/{trip_id}/stops/{stop_id}/items", status_code=status.HTTP_201_CREATED)
def add_item(trip_id: str, stop_id: str, payload: ItemCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); stop = db.query(TripStop).filter_by(id=stop_id, trip_id=trip.id).first()
    if not stop: raise HTTPException(status_code=404, detail="Stop not found")
    activity = db.query(Activity).filter(Activity.id == payload.activity_id).first() if payload.activity_id else None
    if activity and activity.city_id != stop.city_id: raise HTTPException(status_code=422, detail="Activity belongs to another city")
    if not activity and not payload.name: raise HTTPException(status_code=422, detail="Choose an activity or provide a name")
    days = (stop.end_date - stop.start_date).days + 1
    if payload.day_index > days: raise HTTPException(status_code=422, detail="day_index falls outside this stop")
    if activity and any(row.activity_id == activity.id for row in stop.items): raise HTTPException(status_code=409, detail="This activity is already in the destination itinerary")
    slot = _available_time(db, stop, payload.day_index, float(activity.duration_hours or 1) if activity else 1, payload.time_slot)
    item = ItineraryItem(stop_id=stop.id, activity_id=activity.id if activity else None, name=payload.name or activity.name,
        day_index=payload.day_index, sequence=(max((row.sequence for row in stop.items), default=0)//10+1)*10,
        time_slot=slot, cost=payload.cost if payload.cost is not None else float(activity.cost or 0) if activity else 0, notes=payload.notes)
    db.add(item); db.flush(); recalculate_budget(db, trip); db.commit(); db.refresh(item); return item_dict(item, activity)


@router.patch("/{trip_id}/stops/{stop_id}/items/{item_id}")
def update_item(trip_id: str, stop_id: str, item_id: str, payload: ItemUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); stop = db.query(TripStop).filter_by(id=stop_id, trip_id=trip.id).first()
    item = db.query(ItineraryItem).filter_by(id=item_id, stop_id=stop_id).first() if stop else None
    if not item: raise HTTPException(status_code=404, detail="Itinerary item not found")
    values = payload.model_dump(exclude_unset=True)
    if values.get("day_index", item.day_index) > (stop.end_date-stop.start_date).days+1: raise HTTPException(status_code=422, detail="day_index falls outside this stop")
    activity = db.query(Activity).filter(Activity.id == item.activity_id).first()
    day_index = values.get("day_index", item.day_index)
    if "time_slot" in values or "day_index" in values:
        values["time_slot"] = _available_time(db, stop, day_index, float(activity.duration_hours or 1) if activity else 1, values.get("time_slot", item.time_slot), item.id)
    for key, value in values.items(): setattr(item, key, value)
    recalculate_budget(db, trip); db.commit(); db.refresh(item); return item_dict(item, db.query(Activity).filter(Activity.id == item.activity_id).first())


@router.delete("/{trip_id}/stops/{stop_id}/items/{item_id}")
def delete_item(trip_id: str, stop_id: str, item_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); item = db.query(ItineraryItem).join(TripStop).filter(ItineraryItem.id == item_id, TripStop.id == stop_id, TripStop.trip_id == trip.id).first()
    if not item: raise HTTPException(status_code=404, detail="Itinerary item not found")
    db.delete(item); db.flush(); recalculate_budget(db, trip); db.commit(); return {"deleted": True}


@router.post("/{trip_id}/stops/{stop_id}/items/reorder")
def reorder_items(trip_id: str, stop_id: str, payload: ReorderIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); rows = db.query(ItineraryItem).join(TripStop).filter(TripStop.id == stop_id, TripStop.trip_id == trip.id).all(); row_map = {row.id: row for row in rows}
    if set(payload.ordered_ids) != set(row_map): raise HTTPException(status_code=422, detail="ordered_ids must contain every item exactly once")
    for index, row_id in enumerate(payload.ordered_ids, 1): row_map[row_id].sequence = index * 10
    db.commit(); return stop_dict(db, db.query(TripStop).filter_by(id=stop_id).one())


@router.get("/{trip_id}/budget")
def budget(trip_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); items = db.query(ItineraryItem).join(TripStop).filter(TripStop.trip_id == trip.id).all(); expenses = db.query(TripExpense).filter_by(trip_id=trip.id).all()
    categories = defaultdict(float); per_day = defaultdict(float)
    for item in items:
        categories["activities"] += float(item.cost or 0)
        stop = next((row for row in trip.stops if row.id == item.stop_id), None)
        if stop: per_day[str(stop.start_date + timedelta(days=item.day_index-1))] += float(item.cost or 0)
    for expense in expenses:
        categories[expense.category] += float(expense.amount or 0)
        if expense.expense_date: per_day[str(expense.expense_date)] += float(expense.amount or 0)
    total = round(sum(categories.values()), 2); days = max((trip.end_date-trip.start_date).days+1, 1)
    return {"trip_id": trip.id, "total": total, "limit": trip.budget_limit, "remaining": round(trip.budget_limit-total,2) if trip.budget_limit is not None else None,
            "average_per_day": round(total/days,2), "categories": {key: round(value,2) for key,value in categories.items()},
            "per_day": {key: round(value,2) for key,value in sorted(per_day.items())}, "expenses": [{"id":e.id,"category":e.category,"label":e.label,"amount":e.amount,"expense_date":e.expense_date,"stop_id":e.stop_id,"notes":e.notes} for e in expenses]}


@router.post("/{trip_id}/expenses", status_code=status.HTTP_201_CREATED)
def add_expense(trip_id: str, payload: ExpenseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); expense = TripExpense(trip_id=trip.id, **payload.model_dump()); db.add(expense); db.flush(); recalculate_budget(db, trip); db.commit(); db.refresh(expense); return {"id":expense.id, **payload.model_dump()}


@router.patch("/{trip_id}/expenses/{expense_id}")
def update_expense(trip_id: str, expense_id: str, payload: ExpenseUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = owned_trip(db, trip_id, user); expense = db.query(TripExpense).filter_by(id=expense_id, trip_id=trip.id).first()
    if not expense: raise HTTPException(status_code=404, detail="Expense not found")
    for key,value in payload.model_dump(exclude_unset=True).items(): setattr(expense,key,value)
    recalculate_budget(db,trip); db.commit(); db.refresh(expense); return {"id":expense.id,"category":expense.category,"label":expense.label,"amount":expense.amount,"expense_date":expense.expense_date,"stop_id":expense.stop_id,"notes":expense.notes}


@router.delete("/{trip_id}/expenses/{expense_id}")
def delete_expense(trip_id: str, expense_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip=owned_trip(db,trip_id,user); expense=db.query(TripExpense).filter_by(id=expense_id,trip_id=trip.id).first()
    if not expense: raise HTTPException(status_code=404,detail="Expense not found")
    db.delete(expense); db.flush(); recalculate_budget(db,trip); db.commit(); return {"deleted":True}
