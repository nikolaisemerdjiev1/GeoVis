from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import models
from .db import Base, SessionLocal, engine
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path == "/api/ingest/game":
        external_game_id = None
        try:
            body = await request.json()
            if isinstance(body, dict):
                external_game_id = body.get("external_game_id") or body.get("game_id")
        except Exception:
            pass

        db = SessionLocal()
        try:
            db.add(
                models.ImportEvent(
                    external_game_id=external_game_id,
                    status="error",
                    source="extension",
                    message="Validation failed for ingest payload",
                )
            )
            db.commit()
        finally:
            db.close()

    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "geovis-api"}
