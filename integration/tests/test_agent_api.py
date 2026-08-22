from copy import deepcopy
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import models  # noqa: F401
from backend.auth import get_current_user
from backend.database import Base, get_db
from backend.models.activity import Activity
from backend.models.ai_proposal import AIProposal
from backend.models.city import City
from backend.models.itinerary_item import ItineraryItem
from backend.models.trip import Trip
from backend.models.trip_stop import TripStop
from backend.routers import agent_router
from ai_agent.llm_planner import PlannerUnavailableError


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
app = FastAPI()
app.include_router(agent_router.router)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
app.dependency_overrides[get_current_user] = lambda: type("TestUser", (), {"id": "demo"})()
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def seed_trip(*, with_stop=True):
    with TestingSession() as db:
        trip = Trip(id="trip-1", name="Paris", owner_id="demo", start_date=date(2026, 9, 1), end_date=date(2026, 9, 2))
        city = City(id="paris", name="Paris", country="France")
        db.add_all([trip, city])
        if with_stop:
            db.add(TripStop(id="stop-1", trip_id="trip-1", city_id="paris", start_date=date(2026, 9, 1), end_date=date(2026, 9, 2)))
            db.add_all([
                Activity(id="museum", city_id="paris", name="Museum", category="culture", cost=20, duration_hours=3),
                Activity(id="food", city_id="paris", name="Food Tour", category="food", cost=50, duration_hours=2),
            ])
        db.commit()


def create_proposal():
    return client.post(
        "/api/v1/trips/trip-1/planner/proposals",
        json={"goal":"balanced","preferences":["culture","food"],"daily_budget":100,"use_llm":False},
    )


def test_unknown_trip_and_trip_without_stops():
    response = client.post("/api/v1/trips/missing/planner/proposals", json={"use_llm":False})
    assert response.status_code == 404
    seed_trip(with_stop=False)
    response = create_proposal()
    assert response.status_code == 422
    assert "at least one stop" in response.json()["detail"]


def test_create_get_apply_and_reapply_rule_proposal():
    seed_trip()
    created = create_proposal()
    assert created.status_code == 201
    proposal = created.json()
    assert proposal["source"] == "rules"
    assert proposal["status"] == "ready"
    assert proposal["estimated_total"] == 70
    with TestingSession() as db:
        assert db.query(ItineraryItem).count() == 0

    fetched = client.get(f"/api/v1/trips/trip-1/planner/proposals/{proposal['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["items"] == proposal["items"]

    applied = client.post(f"/api/v1/trips/trip-1/planner/proposals/{proposal['id']}/apply")
    assert applied.status_code == 200
    assert applied.json()["status"] == "applied"
    assert applied.json()["total_budget"] == 70

    duplicate = client.post(f"/api/v1/trips/trip-1/planner/proposals/{proposal['id']}/apply")
    assert duplicate.status_code == 409
    with TestingSession() as db:
        assert db.query(ItineraryItem).count() == 2


def test_invalid_saved_proposal_does_not_partially_apply():
    seed_trip()
    proposal_id = create_proposal().json()["id"]
    with TestingSession() as db:
        record = db.query(AIProposal).filter_by(id=proposal_id).one()
        data = deepcopy(record.proposal_data)
        data["items"][0]["activity_id"] = "missing"
        record.proposal_data = data
        db.commit()
    response = client.post(f"/api/v1/trips/trip-1/planner/proposals/{proposal_id}/apply")
    assert response.status_code == 422
    with TestingSession() as db:
        assert db.query(ItineraryItem).count() == 0


def test_gemini_failure_falls_back_to_rules(monkeypatch):
    seed_trip()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("AI_ENABLED", "true")

    def unavailable(*args, **kwargs):
        raise PlannerUnavailableError("simulated invalid model output")

    monkeypatch.setattr("backend.services.ai_service.generate_llm_proposal", unavailable)
    response = client.post(
        "/api/v1/trips/trip-1/planner/proposals",
        json={"goal":"balanced","preferences":["culture"],"use_llm":True},
    )
    assert response.status_code == 201
    assert response.json()["source"] == "rules"
    assert any("rule-based" in warning for warning in response.json()["warnings"])


def test_malformed_saved_proposal_returns_422():
    seed_trip()
    proposal_id = create_proposal().json()["id"]
    with TestingSession() as db:
        record = db.query(AIProposal).filter_by(id=proposal_id).one()
        record.proposal_data = {"not": "a planner proposal"}
        db.commit()
    response = client.post(f"/api/v1/trips/trip-1/planner/proposals/{proposal_id}/apply")
    assert response.status_code == 422
    with TestingSession() as db:
        assert db.query(ItineraryItem).count() == 0
