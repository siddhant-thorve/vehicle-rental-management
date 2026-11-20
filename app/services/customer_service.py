import logging
from sqlalchemy.orm import Session

from app.exceptions import ConflictException
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import CustomerCreate

logger = logging.getLogger("customer_audit")


class CustomerService:
    @staticmethod
    def create_customer(db: Session, req: CustomerCreate) -> User:
        if UserRepository.get_by_email(db, req.email):
            raise ConflictException(f"Customer with email '{req.email}' already exists")

        customer = User(
            email=req.email,
            full_name=req.full_name,
            phone=req.phone,
            licence_no=req.licence_no.strip(),
            licence_verified=False,
            is_active=True,
        )
        created = UserRepository.create(db, customer)
        logger.info("AUDIT: Customer created with ID %s", created.id)
        return created
