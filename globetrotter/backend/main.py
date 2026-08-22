from fastapi import FastAPI
from backend.database import Base, engine

app = FastAPI(title="GlobeTrotter API")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}