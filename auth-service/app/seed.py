from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import User
from app.repositories.users import seed_users_if_missing

db = SessionLocal()

def create_seed_users() -> list[User]:
    return [
            User(
                email="admin@rentalapp.com",
                password_hash=hash_password("Admin@123"),
                full_name="System Administrator",
                phone="+919800000001",
                licence_no=None,
                licence_verified=True,
                role="ADMIN",
                branch_id=None,
                is_active=True,
            ),
            User(
                email="staff.mumbai@rentalapp.com",
                password_hash=hash_password("Staff@123"),
                full_name="Mumbai Central Staff",
                phone="+919800000002",
                licence_no=None,
                licence_verified=True,
                role="BRANCH_STAFF",
                branch_id=1,
                is_active=True,
            ),
            User(
                email="staff.delhi@rentalapp.com",
                password_hash=hash_password("Staff@123"),
                full_name="Delhi Hub Staff",
                phone="+919800000003",
                licence_no=None,
                licence_verified=True,
                role="BRANCH_STAFF",
                branch_id=2,
                is_active=True,
            ),
            User(
                email="customer.verified@rentalapp.com",
                password_hash=hash_password("Customer@123"),
                full_name="Rajesh Verma (Verified)",
                phone="+919800000004",
                licence_no="MH0120200012345",
                licence_verified=True,
                role="CUSTOMER",
                branch_id=None,
                is_active=True,
            ),
            User(
                email="customer.unverified@rentalapp.com",
                password_hash=hash_password("Customer@123"),
                full_name="Pooja Sharma (Unverified)",
                phone="+919800000005",
                licence_no="DL0420210098765",
                licence_verified=False,
                role="CUSTOMER",
                branch_id=None,
                is_active=True,
            ),
    ]


try:
    if seed_users_if_missing(db, "admin@rentalapp.com", create_seed_users):
        print("[OK] Auth users seeded successfully.")
    else:
        print("[OK] Auth users already present.")
finally:
    db.close()
