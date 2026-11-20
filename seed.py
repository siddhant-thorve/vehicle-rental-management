import math
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import User, Branch, VehicleCategory, Vehicle, Tariff, Booking, Rental, Invoice
from app.core.security import get_password_hash


def seed_database():
    print("Ensuring tables are created...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter_by(email="admin@rentalapp.com").first():
            print("Database already seeded. Skipping.")
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

        print("Seeding Users...")
        admin = User(
            email="admin@rentalapp.com",
            password_hash=get_password_hash("Admin@123"),
            full_name="System Administrator",
            phone="+919800000001",
            licence_no=None,
            licence_verified=True,
            role="ADMIN",
            branch_id=None,
            is_active=True,
        )
        staff1 = User(
            email="staff.mumbai@rentalapp.com",
            password_hash=get_password_hash("Staff@123"),
            full_name="Mumbai Branch Executive",
            phone="+919800000002",
            licence_no=None,
            licence_verified=True,
            role="BRANCH_STAFF",
            branch_id=b1.id,
            is_active=True,
        )
        staff2 = User(
            email="staff.delhi@rentalapp.com",
            password_hash=get_password_hash("Staff@123"),
            full_name="Delhi Branch Executive",
            phone="+919800000003",
            licence_no=None,
            licence_verified=True,
            role="BRANCH_STAFF",
            branch_id=b2.id,
            is_active=True,
        )
        cust_verified = User(
            email="customer.verified@rentalapp.com",
            password_hash=get_password_hash("Customer@123"),
            full_name="Rahul Sharma",
            phone="+919800000004",
            licence_no="MH012020001234",
            licence_verified=True,
            role="CUSTOMER",
            branch_id=None,
            is_active=True,
        )
        cust_unverified = User(
            email="customer.unverified@rentalapp.com",
            password_hash=get_password_hash("Customer@123"),
            full_name="Amit Verma",
            phone="+919800000005",
            licence_no="DL042021005678",
            licence_verified=False,
            role="CUSTOMER",
            branch_id=None,
            is_active=True,
        )
        db.add_all([admin, staff1, staff2, cust_verified, cust_unverified])
        db.commit()

        print("Seeding Vehicle Categories...")
        cat_hatch = VehicleCategory(name="Hatchback", description="Compact city hatchback", seating_capacity=4)
        cat_sedan = VehicleCategory(name="Sedan", description="Comfortable family sedan", seating_capacity=5)
        cat_suv = VehicleCategory(name="SUV", description="Premium 7-seater SUV", seating_capacity=7)
        cat_scooter = VehicleCategory(name="Scooter", description="Convenient 2-wheeler scooter", seating_capacity=2)
        db.add_all([cat_hatch, cat_sedan, cat_suv, cat_scooter])
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
            effective_from=now - timedelta(days=30),
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
            effective_from=now - timedelta(days=30),
            is_active=True,
        )
        t_suv = Tariff(
            category_id=cat_suv.id,
            hourly_rate=Decimal("250.00"),
            daily_rate=Decimal("3800.00"),
            weekly_rate=Decimal("22000.00"),
            free_km_per_day=Decimal("250.00"),
            extra_km_rate=Decimal("20.00"),
            extra_hour_rate=Decimal("300.00"),
            deposit_amount=Decimal("8000.00"),
            effective_from=now - timedelta(days=30),
            is_active=True,
        )
        t_scooter = Tariff(
            category_id=cat_scooter.id,
            hourly_rate=Decimal("50.00"),
            daily_rate=Decimal("600.00"),
            weekly_rate=Decimal("3500.00"),
            free_km_per_day=Decimal("100.00"),
            extra_km_rate=Decimal("6.00"),
            extra_hour_rate=Decimal("70.00"),
            deposit_amount=Decimal("1000.00"),
            effective_from=now - timedelta(days=30),
            is_active=True,
        )
        db.add_all([t_hatch, t_sedan, t_suv, t_scooter])
        db.commit()

        print("Seeding Vehicles...")
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
        v3 = Vehicle(
            registration_no="MH-01-AB-1003",
            category_id=cat_suv.id,
            branch_id=b1.id,
            make="Mahindra",
            model="XUV700",
            fuel_type="Diesel",
            transmission="Automatic",
            odometer_km=Decimal("31000.00"),
            status="AVAILABLE",
            is_active=True,
        )
        v4 = Vehicle(
            registration_no="DL-01-CD-2001",
            category_id=cat_hatch.id,
            branch_id=b2.id,
            make="Hyundai",
            model="i20",
            fuel_type="Petrol",
            transmission="Manual",
            odometer_km=Decimal("12300.00"),
            status="AVAILABLE",
            is_active=True,
        )
        v5 = Vehicle(
            registration_no="DL-01-CD-2002",
            category_id=cat_suv.id,
            branch_id=b2.id,
            make="Tata",
            model="Harrier",
            fuel_type="Diesel",
            transmission="Manual",
            odometer_km=Decimal("18900.00"),
            status="AVAILABLE",
            is_active=True,
        )
        v6 = Vehicle(
            registration_no="KA-05-EF-3001",
            category_id=cat_scooter.id,
            branch_id=b3.id,
            make="Honda",
            model="Activa 6G",
            fuel_type="Petrol",
            transmission="Automatic",
            odometer_km=Decimal("8400.00"),
            status="AVAILABLE",
            is_active=True,
        )
        db.add_all([v1, v2, v3, v4, v5, v6])
        db.commit()

        print("Seeding Historical Completed Rental & Invoice for Reports...")
        past_pickup = now - timedelta(days=5)
        past_drop = past_pickup + timedelta(days=2)
        bk_past = Booking(
            booking_no="BK-SAMPLE-0001",
            customer_id=cust_verified.id,
            vehicle_id=v1.id,
            branch_id=b1.id,
            pickup_at=past_pickup,
            drop_at=past_drop,
            estimated_amount=Decimal("3600.00"),
            deposit_amount=Decimal("3000.00"),
            refund_amount=Decimal("0.00"),
            status="COMPLETED",
        )
        db.add(bk_past)
        db.commit()

        rental_past = Rental(
            booking_id=bk_past.id,
            actual_pickup_at=past_pickup,
            actual_drop_at=past_drop,
            odometer_out=Decimal("14800.00"),
            odometer_in=Decimal("15200.00"),
            fuel_out=Decimal("100.00"),
            fuel_in=Decimal("100.00"),
            damage_notes="None. Returned clean.",
        )
        db.add(rental_past)
        db.commit()

        subtotal = Decimal("3600.00") + Decimal("1200.00")  # 100 extra km @ 12 = 1200
        tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
        total = subtotal + tax
        dep_adj = Decimal("3000.00")
        payable = total - dep_adj

        inv_past = Invoice(
            rental_id=rental_past.id,
            base_amount=Decimal("3600.00"),
            extra_km_amount=Decimal("1200.00"),
            extra_hour_amount=Decimal("0.00"),
            fuel_charge=Decimal("0.00"),
            damage_charge=Decimal("0.00"),
            tax_amount=tax,
            total_amount=total,
            deposit_adjusted=dep_adj,
            payable_amount=payable,
            generated_at=past_drop,
        )
        db.add(inv_past)
        db.commit()

        print("Seeding successfully completed!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
