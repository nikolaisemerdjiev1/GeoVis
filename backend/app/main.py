from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routes.games import router as games_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GeoVIS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "geovis-api"}
