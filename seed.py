from datetime import datetime, timezone, timedelta
from decimal import Decimal
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import User, Branch, VehicleCategory, Vehicle, Tariff


def seed_phase1_database():
    print("Ensuring database tables are created...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Branch).filter_by(name="Mumbai Central Branch").first():
            print("Database already contains master data. Ready for demo.")
            return

        print("Seeding Branches...")
        b1 = Branch(
            name="Mumbai Central Branch",
            city="Mumbai",
            address="Station Road, Mumbai Central, Mumbai 400008",
            contact_no="+919876543210",
            is_active=True,
        )
        b2 = Branch(
            name="Delhi Airport Hub",
            city="Delhi",
            address="Terminal 3, IGI Airport, New Delhi 110037",
            contact_no="+919876543211",
            is_active=True,
        )
        b3 = Branch(
            name="Bangalore Electronic City",
            city="Bangalore",
            address="Hosur Road, Electronic City Phase 1, Bangalore 560100",
            contact_no="+919876543212",
            is_active=True,
        )
        db.add_all([b1, b2, b3])
        db.commit()

        print("Seeding a verified demo customer...")
        customer = User(
            email="demo.customer@rentalapp.com",
            full_name="Demo Customer",
            phone="+919800000003",
            licence_no="MH012022001234",
            is_active=True,
        )
        db.add(customer)
        db.commit()

        print("Seeding Vehicle Categories...")
        cat_hatch = VehicleCategory(name="Hatchback", description="Compact city hatchback", seating_capacity=4)
        cat_sedan = VehicleCategory(name="Sedan", description="Comfortable family sedan", seating_capacity=5)
        cat_suv = VehicleCategory(name="SUV", description="Premium 7-seater SUV", seating_capacity=7)
        db.add_all([cat_hatch, cat_sedan, cat_suv])
        db.commit()

        print("Seeding Tariffs...")
        now = datetime.now(timezone.utc)
        t_hatch = Tariff(
            category_id=cat_hatch.id,
            hourly_rate=Decimal("120.00"),
            daily_rate=Decimal("1800.00"),
            weekly_rate=Decimal("10000.00"),
            free_km_per_day=Decimal("150.00"),
            extra_km_rate=Decimal("12.00"),
            extra_hour_rate=Decimal("150.00"),
            deposit_amount=Decimal("3000.00"),
            effective_from=now - timedelta(days=5),
            is_active=True,
        )
        t_sedan = Tariff(
            category_id=cat_sedan.id,
            hourly_rate=Decimal("180.00"),
            daily_rate=Decimal("2500.00"),
            weekly_rate=Decimal("14000.00"),
            free_km_per_day=Decimal("200.00"),
            extra_km_rate=Decimal("15.00"),
            extra_hour_rate=Decimal("220.00"),
            deposit_amount=Decimal("5000.00"),
            effective_from=now - timedelta(days=5),
            is_active=True,
        )
        db.add_all([t_hatch, t_sedan])
        db.commit()

        print("Seeding Initial Vehicles...")
        v1 = Vehicle(
            registration_no="MH-01-AB-1001",
            category_id=cat_hatch.id,
            branch_id=b1.id,
            make="Maruti Suzuki",
            model="Swift",
            fuel_type="Petrol",
            transmission="Manual",
            odometer_km=Decimal("15200.00"),
            status="AVAILABLE",
            is_active=True,
        )
        v2 = Vehicle(
            registration_no="MH-01-AB-1002",
            category_id=cat_sedan.id,
            branch_id=b1.id,
            make="Honda",
            model="City",
            fuel_type="Petrol",
            transmission="Automatic",
            odometer_km=Decimal("24500.00"),
            status="AVAILABLE",
            is_active=True,
        )
        db.add_all([v1, v2])
        db.commit()

        print("Phase 1 master data seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_phase1_database()
