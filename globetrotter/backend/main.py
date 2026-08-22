from fastapi import FastAPI
from backend.database import Base, engine
from backend import models  # noqa: F401 — make sure models/__init__.py imports all model files, including user
from backend.routers import auth_router, trip_router, city_router, activity_router

app = FastAPI(title="GlobeTrotter API")

app.include_router(auth_router.router)
app.include_router(trip_router.router)
# app.include_router(city_router.router)
# app.include_router(activity_router.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}