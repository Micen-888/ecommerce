from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pymongo import MongoClient
from pymongo.database import Database

from src.config import settings


def get_pg_engine() -> Engine:
    return create_engine(settings.postgres_url, pool_pre_ping=True)


def get_mongo_db() -> Database:
    client = MongoClient(settings.mongo_uri)
    return client[settings.mongo_db]


def ping_databases() -> dict[str, bool | str]:
    status: dict[str, bool | str] = {}

    try:
        engine = get_pg_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["postgres"] = True
    except Exception as exc:  # pragma: no cover
        status["postgres"] = f"ERROR: {exc}"

    try:
        db = get_mongo_db()
        db.command("ping")
        status["mongodb"] = True
    except Exception as exc:  # pragma: no cover
        status["mongodb"] = f"ERROR: {exc}"

    return status
