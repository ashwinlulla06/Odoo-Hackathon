import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine
from backend import models  # noqa: F401
from backend.routers import admin_router, agent_router, auth_router, catalog_router, public_router, trip_router, trip_v1_router
from backend.database import SessionLocal
from backend.migrations import migrate_existing_schema
from backend.seed import seed_catalog

app = FastAPI(title="GlobeTrotter API")


def validate_runtime_configuration() -> None:
    if os.getenv("ENVIRONMENT", "development").lower() != "production":
        return
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32 or secret == "change-this-secret-before-deployment":
        raise RuntimeError("JWT_SECRET must be a unique value of at least 32 characters in production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ],
    allow_origin_regex=os.getenv(
        "CORS_ORIGIN_REGEX", r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip_router.router)
app.include_router(agent_router.router)
app.include_router(agent_router.status_router)
app.include_router(auth_router.router)
app.include_router(catalog_router.router)
app.include_router(trip_v1_router.router)
app.include_router(public_router.router)
app.include_router(admin_router.router)


@app.on_event("startup")
def on_startup():
    validate_runtime_configuration()
    migrate_existing_schema(engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_catalog(db)


@app.get("/health")
def health_check():
    return {"status": "ok"}
