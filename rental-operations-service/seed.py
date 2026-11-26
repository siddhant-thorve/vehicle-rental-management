from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import (
    MetaData,
    Table,
    create_engine,
    func,
    insert,
    inspect,
    make_url,
    select,
    text,
)

from app.core.config import DATABASE_URL
from app.db.base import Base
from app.db.session import engine as operations_engine
from app.models import entities


ROOT = Path(__file__).resolve().parents[1]


def ensure_database_exists() -> None:
    target_url = make_url(DATABASE_URL)
    if target_url.get_backend_name() != "postgresql":
        return

    database_name = target_url.database
    if not database_name:
        raise RuntimeError("DATABASE_URL must include a database name")

    admin_engine = create_engine(target_url.set(database="postgres"))
    try:
        with admin_engine.connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": database_name},
            ).scalar()
            if not exists:
                quoted_name = admin_engine.dialect.identifier_preparer.quote(
                    database_name
                )
                connection.exec_driver_sql(f"CREATE DATABASE {quoted_name}")
    finally:
        admin_engine.dispose()


def copy_legacy_rental_data(source_url: str) -> None:
    Base.metadata.create_all(bind=operations_engine)
    legacy_engine = create_engine(source_url)
    legacy_metadata = MetaData()
    target_tables = {
        "rentals": Base.metadata.tables["rentals"],
        "invoices": Base.metadata.tables["invoices"],
    }

    try:
        with legacy_engine.connect() as source, operations_engine.begin() as target:
            source_table_names = set(inspect(source).get_table_names())
            tables_to_copy = source_table_names.intersection(target_tables)
            if "invoices" in tables_to_copy and "rentals" not in tables_to_copy:
                raise RuntimeError(
                    "The legacy invoices table exists, but the rentals table is "
                    "missing; cannot migrate invoices without their rentals."
                )
            if not tables_to_copy:
                print("No legacy rental or invoice tables found; nothing to copy.")

            for table_name in ("rentals", "invoices"):
                if table_name not in tables_to_copy:
                    continue

                source_table = Table(
                    table_name, legacy_metadata, autoload_with=source
                )
                target_table = target_tables[table_name]
                unexpected_columns = set(source_table.c.keys()) - set(
                    target_table.c.keys()
                )
                if unexpected_columns:
                    raise RuntimeError(
                        f"Legacy {table_name} table has unsupported columns: "
                        + ", ".join(sorted(unexpected_columns))
                    )

                source_rows = [
                    dict(row)
                    for row in source.execute(select(source_table)).mappings()
                ]
                row_ids = [row["id"] for row in source_rows]
                existing_by_id = {}
                for offset in range(0, len(row_ids), 500):
                    batch_ids = row_ids[offset : offset + 500]
                    existing_rows = target.execute(
                        select(target_table).where(
                            target_table.c.id.in_(batch_ids)
                        )
                    ).mappings()
                    existing_by_id.update(
                        (row["id"], dict(row)) for row in existing_rows
                    )

                rows_to_insert = []
                for row in source_rows:
                    existing = existing_by_id.get(row["id"])
                    if existing is None:
                        rows_to_insert.append(row)
                    elif any(
                        existing[column] != value for column, value in row.items()
                    ):
                        raise RuntimeError(
                            f"Destination {table_name} row id {row['id']} conflicts "
                            "with the legacy record; no changes were committed."
                        )

                if rows_to_insert:
                    target.execute(insert(target_table), rows_to_insert)

            if operations_engine.dialect.name == "postgresql":
                for table_name, target_table in target_tables.items():
                    max_id = target.execute(
                        select(func.max(target_table.c.id))
                    ).scalar()
                    if max_id is None:
                        continue
                    sequence_name = target.execute(
                        text("SELECT pg_get_serial_sequence(:table_name, 'id')"),
                        {"table_name": table_name},
                    ).scalar()
                    if sequence_name:
                        target.execute(
                            text(
                                "SELECT setval(CAST(:sequence_name AS regclass), "
                                ":max_id, true)"
                            ),
                            {"sequence_name": sequence_name, "max_id": max_id},
                        )
    finally:
        legacy_engine.dispose()


def seed() -> None:
    booking_env = dotenv_values(ROOT / "booking-service" / ".env")
    legacy_database_url = booking_env.get("DATABASE_URL")
    if not legacy_database_url:
        raise RuntimeError(
            "DATABASE_URL is missing from booking-service/.env; "
            "cannot copy existing rental data."
        )

    ensure_database_exists()
    copy_legacy_rental_data(legacy_database_url)
    print("Rental Operations seed and legacy data copy completed.")


if __name__ == "__main__":
    seed()
