from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from backend.database import Base, engine
from backend import models  # noqa: F401
from backend.routers import trip_router

app = FastAPI(title="GlobeTrotter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip_router.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}