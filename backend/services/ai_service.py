import os
from datetime import datetime, timezone

from pydantic import ValidationError
from sqlalchemy.orm import Session

from ai_agent.budget_estimator import estimate_total
from ai_agent.llm_planner import PlannerUnavailableError, generate_llm_proposal
from ai_agent.proposal_schema import PlannerProposal
from ai_agent.recommender import build_rule_proposal
from ai_agent.schedule_validator import validate_proposal
from backend.models.activity import Activity
from backend.models.ai_proposal import AIProposal
from backend.models.itinerary_item import ItineraryItem
from backend.models.trip import Trip
from backend.models.trip_stop import TripStop
from backend.schemas.ai_proposal import ProposalCreate


class ProposalInputError(ValueError):
    pass


def _stop_dict(stop: TripStop) -> dict:
    return {"id": stop.id, "city_id": stop.city_id, "start_date": stop.start_date.isoformat(),
            "end_date": stop.end_date.isoformat(), "sequence": stop.sequence}


def _activity_dict(activity: Activity) -> dict:
    return {"id": activity.id, "city_id": activity.city_id, "name": activity.name,
            "category": activity.category, "cost": float(activity.cost or 0),
            "duration_hours": float(activity.duration_hours or 0),
            "description": activity.description}


def _context(db: Session, trip: Trip) -> tuple[list[dict], list[dict]]:
    stops = db.query(TripStop).filter(TripStop.trip_id == trip.id).order_by(TripStop.sequence).all()
    if not stops:
        raise ProposalInputError("Trip must contain at least one stop")
    for stop in stops:
        if stop.start_date > stop.end_date:
            raise ProposalInputError(f"Stop {stop.id} has an invalid date range")
        if stop.start_date < trip.start_date or stop.end_date > trip.end_date:
            raise ProposalInputError(f"Stop {stop.id} falls outside the trip date range")
    city_ids = {stop.city_id for stop in stops}
    activities = db.query(Activity).filter(Activity.city_id.in_(city_ids)).all()
    if not activities:
        raise ProposalInputError("No catalog activities are available for this trip's cities")
    return [_stop_dict(stop) for stop in stops], [_activity_dict(item) for item in activities]


def generate_proposal(db: Session, trip: Trip, request: ProposalCreate) -> AIProposal:
    stops, activities = _context(db, trip)
    request_data = request.model_dump()
    proposal, source, model, fallback_warning = None, "rules", None, None
    ai_enabled = os.getenv("AI_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
    api_key = os.getenv("GEMINI_API_KEY")
    requested_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if request.use_llm and ai_enabled and api_key:
        try:
            proposal = generate_llm_proposal(stops, activities, request_data, api_key=api_key,
                                             model=requested_model, timeout_seconds=25.0)
            errors = validate_proposal(proposal, stops, activities)
            if errors:
                raise ProposalInputError("; ".join(errors))
            source, model = "gemini", requested_model
        except (PlannerUnavailableError, ProposalInputError, ValueError, TypeError) as exc:
            fallback_warning = f"Gemini was unavailable; rule-based planning was used ({exc})"
    elif request.use_llm:
        fallback_warning = "Gemini is not configured; rule-based planning was used"
    if proposal is None:
        proposal = build_rule_proposal(stops, activities, request_data)
        errors = validate_proposal(proposal, stops, activities)
        if errors:
            raise ProposalInputError("Generated proposal is invalid: " + "; ".join(errors))
    proposal = PlannerProposal.model_validate(proposal)
    proposal.estimated_total = estimate_total(proposal.items)
    if fallback_warning:
        proposal.warnings.append(fallback_warning)
    record = AIProposal(trip_id=trip.id, status="ready", source=source, model=model,
                        request_data=request_data, proposal_data=proposal.model_dump(mode="json"))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def serialize_proposal(record: AIProposal) -> dict:
    data = dict(record.proposal_data or {})
    return {"id": record.id, "trip_id": record.trip_id, "status": record.status,
            "source": record.source, "model": record.model,
            "summary": data.get("summary", "Itinerary proposal"),
            "estimated_total": float(data.get("estimated_total", 0)),
            "warnings": data.get("warnings", []), "items": data.get("items", []),
            "created_at": record.created_at, "applied_at": record.applied_at}


def apply_proposal(db: Session, trip: Trip, record: AIProposal) -> list[str]:
    try:
        proposal = PlannerProposal.model_validate(record.proposal_data)
    except (ValidationError, TypeError, ValueError) as exc:
        raise ProposalInputError(f"Stored proposal is invalid: {exc}") from exc
    stops, activities = _context(db, trip)
    errors = validate_proposal(proposal, stops, activities)
    if errors:
        raise ProposalInputError("Proposal is no longer valid: " + "; ".join(errors))
    stop_by_id = {stop.id: stop for stop in db.query(TripStop).filter(TripStop.trip_id == trip.id).all()}
    activity_by_id = {activity.id: activity for activity in db.query(Activity).all()}
    created: list[ItineraryItem] = []
    try:
        affected_stop_ids = {item.stop_id for item in proposal.items}
        db.query(ItineraryItem).filter(ItineraryItem.stop_id.in_(affected_stop_ids)).delete(synchronize_session=False)
        db.flush()
        for proposed in proposal.items:
            activity = activity_by_id[proposed.activity_id]
            item = ItineraryItem(stop_id=proposed.stop_id, activity_id=activity.id, name=activity.name,
                                 day_index=proposed.day_index, sequence=proposed.sequence,
                                 time_slot=proposed.time_slot, cost=float(activity.cost or 0), notes=proposed.notes)
            db.add(item)
            created.append(item)
        db.flush()
        for stop in stop_by_id.values():
            stop.budget_estimate = round(sum(float(item.cost or 0) for item in stop.items), 2)
        db.flush()
        trip.total_budget = round(sum(float(stop.budget_estimate or 0) for stop in stop_by_id.values()), 2)
        record.status, record.applied_at = "applied", datetime.now(timezone.utc)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return [item.id for item in created]
