import importlib.util
from pathlib import Path

from sqlalchemy import inspect

from app.db.models import Base
from app.db.session import build_engine


def load_migration_module():
    migration_path = (
        Path(__file__).resolve().parents[1] / "app" / "db" / "migrations" / "001_init.py"
    )
    spec = importlib.util.spec_from_file_location("migration_001", migration_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_T_01_schema_and_migration_create_required_tables():
    engine = build_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    migration = load_migration_module()
    migration.upgrade(engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "slots" in tables
    assert "bookings" in tables
    assert "audit_logs" in tables

    slot_columns = {column["name"] for column in inspector.get_columns("slots")}
    assert {"id", "slot_date", "start_time", "package_code", "capacity", "remaining", "created_at"}.issubset(slot_columns)

    booking_columns = {column["name"] for column in inspector.get_columns("bookings")}
    assert {"id", "hn", "slot_id", "booking_date", "queue_no", "status", "created_at"}.issubset(booking_columns)
    assert "national_id" not in booking_columns

    audit_columns = {column["name"] for column in inspector.get_columns("audit_logs")}
    assert {"id", "actor_id", "action", "hn", "accessed_at"}.issubset(audit_columns)
