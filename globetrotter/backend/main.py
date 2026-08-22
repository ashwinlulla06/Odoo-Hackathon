from fastapi import FastAPI
from backend.database import Base, engine
from backend import models  # noqa: F401
# 1. ADD THE NEW ROUTERS TO THIS IMPORT LINE:
from backend.routers import trip_router, city_router, activity_router

app = FastAPI(title="GlobeTrotter API")

app.include_router(trip_router.router)
# 2. REGISTER THE NEW ROUTERS HERE:
app.include_router(city_router.router)
app.include_router(activity_router.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}