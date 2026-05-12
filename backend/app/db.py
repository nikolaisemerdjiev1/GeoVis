from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

configured_url = os.environ.get("GEOVIS_DATABASE_URL")
configured_path = os.environ.get("GEOVIS_DB_PATH")

if configured_url:
    DATABASE_URL = configured_url
elif configured_path:
    DB_PATH = Path(configured_path).expanduser().resolve()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = DATA_DIR / "geovis.sqlite3"
    DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
