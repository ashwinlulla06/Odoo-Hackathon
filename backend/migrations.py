"""Small, idempotent compatibility migrations for the hackathon SQLite DB.

Alembic can take over for production deployments; this keeps existing local
demo data usable immediately when new nullable columns are introduced.
"""

from sqlalchemy import inspect, text


def migrate_existing_schema(engine) -> None:
    inspector = inspect(engine)
    if "trips" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("trips")}
    additions = {
        "budget_limit": "FLOAT",
        "created_at": "DATETIME",
        "updated_at": "DATETIME",
    }
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE trips ADD COLUMN {name} {sql_type}"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_trips_owner_id ON trips(owner_id)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_trip_stops_trip_id ON trip_stops(trip_id)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_itinerary_items_stop_id ON itinerary_items(stop_id)"))
        if engine.dialect.name == "sqlite":
            connection.execute(text("PRAGMA optimize"))
