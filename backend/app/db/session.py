import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.db.models import Base  # รองรับ CON-TECH-01


def build_engine(database_url: str | None = None) -> Engine:
    resolved_url = database_url or os.getenv("DATABASE_URL", "sqlite:///:memory:")
    return create_engine(resolved_url, future=True)


def init_db(database_url: str | None = None) -> Engine:
    engine = build_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine
