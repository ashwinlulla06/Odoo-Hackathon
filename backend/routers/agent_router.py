import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models.ai_proposal import AIProposal
from backend.models.trip import Trip
from backend.schemas.ai_proposal import ProposalApplyOut, ProposalCreate, ProposalOut
from backend.services.ai_service import ProposalInputError, apply_proposal, generate_proposal, serialize_proposal
from backend.models.user import User

router = APIRouter(prefix="/api/v1/trips/{trip_id}/planner/proposals", tags=["AI planner"])
status_router = APIRouter(prefix="/api/v1/ai", tags=["AI planner"])


@status_router.get("/status")
def gemini_status(user: User = Depends(get_current_user)):
    enabled = os.getenv("AI_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
    key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if not enabled or not key:
        return {"connected": False, "configured": bool(key), "enabled": enabled, "model": model,
                "message": "Gemini is disabled" if not enabled else "Gemini API key is missing"}
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=5000))
        client.models.get(model=model)
        return {"connected": True, "configured": True, "enabled": True, "model": model,
                "message": "Gemini connected"}
    except Exception as exc:
        return {"connected": False, "configured": True, "enabled": True, "model": model,
                "message": f"Gemini connection failed: {exc}"}


def _trip_or_404(db: Session, trip_id: str, user: User) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.owner_id == user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def _proposal_or_404(db: Session, trip_id: str, proposal_id: str) -> AIProposal:
    proposal = db.query(AIProposal).filter(
        AIProposal.id == proposal_id, AIProposal.trip_id == trip_id
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.post("", response_model=ProposalOut, status_code=status.HTTP_201_CREATED)
def create_proposal(trip_id: str, payload: ProposalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip = _trip_or_404(db, trip_id, user)
    try:
        return serialize_proposal(generate_proposal(db, trip, payload))
    except ProposalInputError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{proposal_id}", response_model=ProposalOut)
def get_proposal(trip_id: str, proposal_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _trip_or_404(db, trip_id, user)
    return serialize_proposal(_proposal_or_404(db, trip_id, proposal_id))


@router.post("/{proposal_id}/apply", response_model=ProposalApplyOut)
def apply_saved_proposal(trip_id: str, proposal_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    trip = _trip_or_404(db, trip_id, user)
    proposal = _proposal_or_404(db, trip_id, proposal_id)
    if proposal.status == "applied":
        raise HTTPException(status_code=409, detail="Proposal has already been applied")
    if proposal.status != "ready":
        raise HTTPException(status_code=409, detail="Proposal is not ready to apply")
    try:
        item_ids = apply_proposal(db, trip, proposal)
    except ProposalInputError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.refresh(trip)
    return {"proposal_id": proposal.id, "trip_id": trip.id, "status": "applied",
            "created_item_ids": item_ids, "total_budget": float(trip.total_budget or 0)}
