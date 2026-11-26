from decimal import Decimal

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.entities import Tariff, VehicleCategory
from app.repositories.catalog import seed_records_if_empty

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    categories = [
        VehicleCategory(
            id=1,
            name="Hatchback",
            description="Economical 5-seater city car",
            seating_capacity=5,
        ),
        VehicleCategory(
            id=2,
            name="Sedan",
            description="Comfortable 5-seater executive sedan",
            seating_capacity=5,
        ),
        VehicleCategory(
            id=3,
            name="SUV",
            description="Spacious 7-seater premium SUV",
            seating_capacity=7,
        ),
    ]
    if seed_records_if_empty(db, categories):
        print("[OK] Vehicle categories seeded.")

    tariffs = [
        Tariff(
            id=1,
            category_id=1,
            hourly_rate=Decimal("120.00"),
            daily_rate=Decimal("1500.00"),
            weekly_rate=Decimal("8500.00"),
            free_km_per_day=Decimal("200.00"),
            extra_km_rate=Decimal("12.00"),
            extra_hour_rate=Decimal("150.00"),
            deposit_amount=Decimal("3000.00"),
        ),
        Tariff(
            id=2,
            category_id=2,
            hourly_rate=Decimal("180.00"),
            daily_rate=Decimal("2200.00"),
            weekly_rate=Decimal("12000.00"),
            free_km_per_day=Decimal("250.00"),
            extra_km_rate=Decimal("15.00"),
            extra_hour_rate=Decimal("200.00"),
            deposit_amount=Decimal("5000.00"),
        ),
        Tariff(
            id=3,
            category_id=3,
            hourly_rate=Decimal("250.00"),
            daily_rate=Decimal("3200.00"),
            weekly_rate=Decimal("18000.00"),
            free_km_per_day=Decimal("300.00"),
            extra_km_rate=Decimal("20.00"),
            extra_hour_rate=Decimal("300.00"),
            deposit_amount=Decimal("7000.00"),
        ),
    ]
    if seed_records_if_empty(db, tariffs):
        print("[OK] Tariffs seeded.")
finally:
    db.close()
