from typing import Optional
from sqlalchemy.orm import Session
import logging

from app.models.user import User
from app.schemas.user import CustomerRegisterRequest, StaffCreateRequest, LoginRequest, TokenResponse, UserRole
from app.repositories.user_repo import UserRepository
from app.repositories.branch_repo import BranchRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.exceptions import ConflictException, NotFoundException, UnauthorizedException, BadRequestException

logger = logging.getLogger("auth_audit")


class AuthService:
    @staticmethod
    def register_customer(db: Session, req: CustomerRegisterRequest) -> User:
        existing = UserRepository.get_by_email(db, req.email)
        if existing:
            raise ConflictException(f"User with email '{req.email}' already exists")

        user = User(
            email=req.email,
            password_hash=get_password_hash(req.password),
            full_name=req.full_name,
            phone=req.phone,
            licence_no=req.licence_no.strip(),
            licence_verified=False,
            role=UserRole.CUSTOMER.value,
            branch_id=None,
            is_active=True,
        )
        created = UserRepository.create(db, user)
        logger.info(f"AUDIT: Customer registered with ID {created.id}")
        return created

    @staticmethod
    def create_branch_staff(db: Session, req: StaffCreateRequest) -> User:
        branch = BranchRepository.get_by_id(db, req.branch_id)
        if not branch or not branch.is_active:
            raise NotFoundException(f"Branch with ID {req.branch_id} not found or inactive")

        existing = UserRepository.get_by_email(db, req.email)
        if existing:
            raise ConflictException(f"User with email '{req.email}' already exists")

        user = User(
            email=req.email,
            password_hash=get_password_hash(req.password),
            full_name=req.full_name,
            phone=req.phone,
            licence_no=None,
            licence_verified=False,
            role=UserRole.BRANCH_STAFF.value,
            branch_id=req.branch_id,
            is_active=True,
        )
        created = UserRepository.create(db, user)
        logger.info(f"AUDIT: Branch staff created with ID {created.id} for Branch {req.branch_id}")
        return created

    @staticmethod
    def verify_licence(db: Session, customer_id: int) -> User:
        customer = UserRepository.get_by_id(db, customer_id)
        if not customer:
            raise NotFoundException(f"Customer with ID {customer_id} not found")
        if customer.role != UserRole.CUSTOMER.value:
            raise BadRequestException("User is not a customer")
        if not customer.licence_no:
            raise BadRequestException("Customer has no driving licence submitted")

        customer.licence_verified = True
        updated = UserRepository.update(db, customer)
        logger.info(f"AUDIT: Customer ID {customer_id} licence verified")
        return updated

    @staticmethod
    def login(db: Session, req: LoginRequest) -> TokenResponse:
        user = UserRepository.get_by_email(db, req.email)
        if not user or not verify_password(req.password, user.password_hash):
            logger.warning(f"AUDIT: Failed login attempt for email {req.email}")
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        token_data = {
            "sub": str(user.id),
            "role": user.role,
            "branch_id": user.branch_id,
        }
        token = create_access_token(data=token_data)
        logger.info(f"AUDIT: Successful login for User ID {user.id} ({user.role})")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role=user.role,
            user_id=user.id,
        )
