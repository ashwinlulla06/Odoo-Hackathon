from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import models  # noqa: F401
from backend.database import Base, get_db
from backend.models.activity import Activity
from backend.models.city import City
from backend.routers import admin_router, auth_router, catalog_router, public_router, trip_v1_router

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
app = FastAPI()
for router in (auth_router.router, catalog_router.router, trip_v1_router.router, public_router.router, admin_router.router):
    app.include_router(router)

def db_override():
    with Session() as db:
        yield db

app.dependency_overrides[get_db] = db_override
client = TestClient(app)

@pytest.fixture(autouse=True)
def database(monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", "admin@example.com")
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    with Session() as db:
        db.add(City(id="delhi", name="Delhi", country="India", cost_index=0.72, popularity=99))
        db.add(Activity(id="museum", city_id="delhi", name="City Museum", category="culture", cost=25, duration_hours=2))
        db.commit()
    yield

def signup(email="traveller@example.com"):
    response = client.post("/api/v1/auth/signup", json={"email":email,"password":"secretpass","first_name":"Alex","last_name":"Kumar"})
    assert response.status_code == 201
    return {"Authorization":f"Bearer {response.json()['access_token']}"}

def test_authenticated_trip_itinerary_budget_publish_and_copy():
    headers = signup()
    trip = client.post("/api/v1/trips", headers=headers, json={"name":"Delhi Days","start_date":"2026-09-01","end_date":"2026-09-03","budget_limit":500}).json()
    stop = client.post(f"/api/v1/trips/{trip['id']}/stops", headers=headers, json={"city_id":"delhi","start_date":"2026-09-01","end_date":"2026-09-03"})
    assert stop.status_code == 201
    item = client.post(f"/api/v1/trips/{trip['id']}/stops/{stop.json()['id']}/items", headers=headers, json={"activity_id":"museum","day_index":1,"time_slot":"10:00"})
    assert item.status_code == 201
    expense = client.post(f"/api/v1/trips/{trip['id']}/expenses", headers=headers, json={"category":"transport","label":"Airport train","amount":35,"expense_date":"2026-09-01"})
    assert expense.status_code == 201
    budget = client.get(f"/api/v1/trips/{trip['id']}/budget", headers=headers).json()
    assert budget["total"] == 60 and budget["remaining"] == 440
    published = client.post(f"/api/v1/trips/{trip['id']}/publish", headers=headers)
    assert published.status_code == 200
    slug = published.json()["share_slug"]
    assert client.get(f"/api/v1/public/trips/{slug}").status_code == 200
    copied = client.post(f"/api/v1/public/trips/{slug}/copy", headers=headers)
    assert copied.status_code == 201 and copied.json()["name"].endswith("My copy")

def test_login_ownership_and_admin_guard():
    owner = signup("owner@example.com")
    trip = client.post("/api/v1/trips", headers=owner, json={"name":"Private","start_date":"2026-10-01","end_date":"2026-10-02"}).json()
    other = signup("other@example.com")
    assert client.get(f"/api/v1/trips/{trip['id']}", headers=other).status_code == 404
    assert client.get("/api/v1/admin/analytics", headers=other).status_code == 403
    admin = signup("admin@example.com")
    analytics = client.get("/api/v1/admin/analytics", headers=admin)
    assert analytics.status_code == 200 and analytics.json()["totals"]["users"] == 3
    login = client.post("/api/v1/auth/login", json={"email":"owner@example.com","password":"secretpass"})
    assert login.status_code == 200
    assert client.post("/api/v1/auth/login", json={"email":"owner@example.com","password":"wrongpass"}).status_code == 401
