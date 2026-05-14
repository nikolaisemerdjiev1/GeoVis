from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException

from ..db import DATABASE_URL


def sqlite_database_path() -> Path | None:
    prefix = "sqlite:///"
    if not DATABASE_URL.startswith(prefix):
        return None
    return Path(DATABASE_URL.removeprefix(prefix)).resolve()


def create_sqlite_backup() -> Path:
    source_path = sqlite_database_path()
    if source_path is None:
        raise HTTPException(status_code=400, detail="SQLite backup is only available for file-backed SQLite databases")
    if not source_path.exists():
        raise HTTPException(status_code=404, detail="SQLite database file does not exist yet")

    export_dir = source_path.parent / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_path = export_dir / f"geovis-backup-{timestamp}.sqlite3"

    source = sqlite3.connect(source_path)
    try:
        backup = sqlite3.connect(backup_path)
        try:
            source.backup(backup)
        finally:
            backup.close()
    finally:
        source.close()

    return backup_path
