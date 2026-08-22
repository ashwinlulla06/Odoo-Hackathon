from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine
from backend import models  # noqa: F401
from backend.routers import auth_router, trip_router, city_router, activity_router, public_router

app = FastAPI(title="GlobeTrotter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All Routers (Manthan's + Ours)
app.include_router(auth_router.router)
app.include_router(trip_router.router)
app.include_router(city_router.router)
app.include_router(activity_router.router)
app.include_router(public_router.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}