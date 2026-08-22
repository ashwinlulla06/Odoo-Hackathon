from fastapi import FastAPI
from backend.database import Base, engine
from backend import models  # noqa: F401
from backend.routers import trip_router

app = FastAPI(title="GlobeTrotter API")

app.include_router(trip_router.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}