from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    licence_no = Column(String(50), nullable=True)
    licence_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="CUSTOMER", nullable=False)  # ADMIN, BRANCH_STAFF, CUSTOMER
    branch_id = Column(Integer, nullable=True)  # Applicable only for BRANCH_STAFF
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
