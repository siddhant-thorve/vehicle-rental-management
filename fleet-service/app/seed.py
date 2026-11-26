from decimal import Decimal

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.entities import Branch, Vehicle
from app.repositories.fleet import seed_records_if_empty

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    branches = [
        Branch(name="Mumbai Central Branch", city="Mumbai", address="Station Road, Mumbai 400008", contact_no="+919876543210"),
        Branch(name="Delhi Airport Hub", city="Delhi", address="Terminal 3, IGI Airport, New Delhi 110037", contact_no="+919876543211"),
        Branch(name="Bangalore Electronic City", city="Bangalore", address="Hosur Road, Phase 1, Bangalore 560100", contact_no="+919876543212"),
    ]
    if seed_records_if_empty(db, branches):
        print("[OK] Branches seeded.")

    vehicles = [
        Vehicle(
            registration_no="MH-01-AB-1001",
            category_id=1,
            branch_id=1,
            make="Maruti Suzuki",
            model="Swift VXi",
            fuel_type="Petrol",
            transmission="Manual",
            odometer_km=Decimal("15000.00"),
            status="AVAILABLE",
        ),
        Vehicle(
            registration_no="MH-01-AB-1002",
            category_id=2,
            branch_id=1,
            make="Hyundai",
            model="Verna SX",
            fuel_type="Diesel",
            transmission="Automatic",
            odometer_km=Decimal("22000.00"),
            status="AVAILABLE",
        ),
        Vehicle(
            registration_no="DL-01-XY-2001",
            category_id=3,
            branch_id=2,
            make="Mahindra",
            model="XUV700 AX7",
            fuel_type="Diesel",
            transmission="Automatic",
            odometer_km=Decimal("8500.00"),
            status="AVAILABLE",
        ),
    ]
    if seed_records_if_empty(db, vehicles):
        print("[OK] Vehicles seeded.")
finally:
    db.close()
