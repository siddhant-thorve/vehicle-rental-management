from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
import logging

from app.models.vehicle import VehicleCategory, Vehicle
from app.schemas.vehicle import CategoryCreate, VehicleCreate, VehicleStatus
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.branch_repo import BranchRepository
from app.exceptions import NotFoundException, ConflictException

logger = logging.getLogger("vehicle_audit")


class VehicleService:
    # --- Vehicle Categories ---
    @staticmethod
    def create_category(db: Session, req: CategoryCreate) -> VehicleCategory:
        existing = VehicleRepository.get_category_by_name(db, req.name)
        if existing:
            raise ConflictException(f"Category '{req.name}' already exists")

        cat = VehicleCategory(
            name=req.name,
            description=req.description,
            seating_capacity=req.seating_capacity,
            is_active=True,
        )
        created = VehicleRepository.create_category(db, cat)
        logger.info(f"AUDIT: Vehicle Category created with ID {created.id}")
        return created

    @staticmethod
    def list_categories(
        db: Session,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 50,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> Tuple[List[VehicleCategory], int]:
        skip = (page - 1) * size
        return VehicleRepository.list_categories(
            db=db,
            is_active=is_active,
            skip=skip,
            limit=size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

    # --- Vehicles ---
    @staticmethod
    def create_vehicle(db: Session, req: VehicleCreate) -> Vehicle:
        branch = BranchRepository.get_by_id(db, req.branch_id)
        if not branch or not branch.is_active:
            raise NotFoundException(f"Branch ID {req.branch_id} not found or inactive")

        category = VehicleRepository.get_category_by_id(db, req.category_id)
        if not category or not category.is_active:
            raise NotFoundException(f"Category ID {req.category_id} not found or inactive")

        existing = VehicleRepository.get_vehicle_by_reg_no(db, req.registration_no)
        if existing:
            raise ConflictException(f"Vehicle with registration '{req.registration_no}' already exists")

        vehicle = Vehicle(
            registration_no=req.registration_no.strip().upper(),
            category_id=req.category_id,
            branch_id=req.branch_id,
            make=req.make,
            model=req.model,
            fuel_type=req.fuel_type,
            transmission=req.transmission,
            odometer_km=req.odometer_km,
            status=VehicleStatus.AVAILABLE.value,
            is_active=True,
        )
        created = VehicleRepository.create_vehicle(db, vehicle)
        logger.info(f"AUDIT: Vehicle created with ID {created.id} (Reg: {created.registration_no})")
        return created

    @staticmethod
    def list_vehicles(
        db: Session,
        branch_id: Optional[int] = None,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> Tuple[List[Vehicle], int]:
        skip = (page - 1) * size
        return VehicleRepository.list_vehicles(
            db=db,
            branch_id=branch_id,
            category_id=category_id,
            status=status,
            is_active=is_active,
            skip=skip,
            limit=size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
