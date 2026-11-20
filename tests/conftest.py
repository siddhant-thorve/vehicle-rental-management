import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models import User, Branch, VehicleCategory, Vehicle, Tariff, Booking, Rental, Invoice
from app.core.security import get_password_hash, create_access_token

# SQLite in-memory database with StaticPool for thread-safe test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_test_data(db_session):
    # Branches
    b1 = Branch(name="Mumbai Branch", city="Mumbai", address="Mumbai Central", contact_no="9876543210")
    b2 = Branch(name="Delhi Branch", city="Delhi", address="Connaught Place", contact_no="9876543211")
    db_session.add_all([b1, b2])
    db_session.commit()

    # Users
    admin = User(
        email="admin@test.com",
        password_hash=get_password_hash("AdminPass123"),
        full_name="Admin User",
        phone="9800000001",
        licence_no=None,
        licence_verified=True,
        role="ADMIN",
        branch_id=None,
        is_active=True,
    )
    staff1 = User(
        email="staff1@test.com",
        password_hash=get_password_hash("StaffPass123"),
        full_name="Staff Branch 1",
        phone="9800000002",
        licence_no=None,
        licence_verified=True,
        role="BRANCH_STAFF",
        branch_id=b1.id,
        is_active=True,
    )
    staff2 = User(
        email="staff2@test.com",
        password_hash=get_password_hash("StaffPass123"),
        full_name="Staff Branch 2",
        phone="9800000003",
        licence_no=None,
        licence_verified=True,
        role="BRANCH_STAFF",
        branch_id=b2.id,
        is_active=True,
    )
    cust_verified = User(
        email="verified@test.com",
        password_hash=get_password_hash("CustPass123"),
        full_name="Verified Customer",
        phone="9800000004",
        licence_no="MH012020009999",
        licence_verified=True,
        role="CUSTOMER",
        branch_id=None,
        is_active=True,
    )
    cust_unverified = User(
        email="unverified@test.com",
        password_hash=get_password_hash("CustPass123"),
        full_name="Unverified Customer",
        phone="9800000005",
        licence_no="DL042021008888",
        licence_verified=False,
        role="CUSTOMER",
        branch_id=None,
        is_active=True,
    )
    db_session.add_all([admin, staff1, staff2, cust_verified, cust_unverified])
    db_session.commit()

    # Category & Tariff
    cat = VehicleCategory(name="Hatchback", description="Economy Car", seating_capacity=4)
    db_session.add(cat)
    db_session.commit()

    now = datetime.now(timezone.utc)
    tariff = Tariff(
        category_id=cat.id,
        hourly_rate=Decimal("100.00"),
        daily_rate=Decimal("1500.00"),
        weekly_rate=Decimal("7000.00"),
        free_km_per_day=Decimal("150.00"),
        extra_km_rate=Decimal("10.00"),
        extra_hour_rate=Decimal("120.00"),
        deposit_amount=Decimal("3000.00"),
        effective_from=now - timedelta(days=1),
        is_active=True,
    )
    db_session.add(tariff)
    db_session.commit()

    # Vehicle in Branch 1
    veh1 = Vehicle(
        registration_no="MH-01-TEST-001",
        category_id=cat.id,
        branch_id=b1.id,
        make="Hyundai",
        model="i10",
        fuel_type="Petrol",
        transmission="Manual",
        odometer_km=Decimal("10000.00"),
        status="AVAILABLE",
        is_active=True,
    )
    # Vehicle in Branch 2
    veh2 = Vehicle(
        registration_no="DL-01-TEST-002",
        category_id=cat.id,
        branch_id=b2.id,
        make="Maruti",
        model="Swift",
        fuel_type="Petrol",
        transmission="Manual",
        odometer_km=Decimal("20000.00"),
        status="AVAILABLE",
        is_active=True,
    )
    db_session.add_all([veh1, veh2])
    db_session.commit()

    return {
        "b1": b1,
        "b2": b2,
        "admin": admin,
        "staff1": staff1,
        "staff2": staff2,
        "cust_verified": cust_verified,
        "cust_unverified": cust_unverified,
        "category": cat,
        "tariff": tariff,
        "veh1": veh1,
        "veh2": veh2,
    }


def make_token(user: User) -> str:
    return create_access_token({
        "sub": str(user.id),
        "role": user.role,
        "branch_id": user.branch_id,
    })


@pytest.fixture
def admin_headers(seed_test_data):
    token = make_token(seed_test_data["admin"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff1_headers(seed_test_data):
    token = make_token(seed_test_data["staff1"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff2_headers(seed_test_data):
    token = make_token(seed_test_data["staff2"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(seed_test_data):
    token = make_token(seed_test_data["cust_verified"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def unverified_headers(seed_test_data):
    token = make_token(seed_test_data["cust_unverified"])
    return {"Authorization": f"Bearer {token}"}
