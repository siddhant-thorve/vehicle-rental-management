from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, asc
from app.models.vehicle import VehicleCategory, Vehicle


class VehicleRepository:
    # --- Categories ---
    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional[VehicleCategory]:
        return db.get(VehicleCategory, category_id)

    @staticmethod
    def get_category_by_name(db: Session, name: str) -> Optional[VehicleCategory]:
        stmt = select(VehicleCategory).where(VehicleCategory.name.ilike(name))
        return db.scalars(stmt).first()

    @staticmethod
    def create_category(db: Session, category: VehicleCategory) -> VehicleCategory:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod   
    def list_categories(
        db: Session,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> Tuple[List[VehicleCategory], int]:
        stmt = select(VehicleCategory)
        count_stmt = select(func.count(VehicleCategory.id))

        if is_active is not None:
            stmt = stmt.where(VehicleCategory.is_active == is_active)
            count_stmt = count_stmt.where(VehicleCategory.is_active == is_active)

        sort_col = getattr(VehicleCategory, sort_by, VehicleCategory.id)
        stmt = stmt.order_by(desc(sort_col) if sort_dir.lower() == "desc" else asc(sort_col))

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total

    # --- Vehicles ---
    @staticmethod
    def get_vehicle_by_reg_no(db: Session, registration_no: str) -> Optional[Vehicle]:
        stmt = select(Vehicle).where(Vehicle.registration_no == registration_no)
        return db.scalars(stmt).first()

    @staticmethod
    def create_vehicle(db: Session, vehicle: Vehicle) -> Vehicle:
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
        return vehicle

    @staticmethod
    def list_vehicles(
        db: Session,
        branch_id: Optional[int] = None,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> Tuple[List[Vehicle], int]:
        stmt = select(Vehicle)
        count_stmt = select(func.count(Vehicle.id))

        if branch_id:
            stmt = stmt.where(Vehicle.branch_id == branch_id)
            count_stmt = count_stmt.where(Vehicle.branch_id == branch_id)
        if category_id:
            stmt = stmt.where(Vehicle.category_id == category_id)
            count_stmt = count_stmt.where(Vehicle.category_id == category_id)
        if status:
            stmt = stmt.where(Vehicle.status == status)
            count_stmt = count_stmt.where(Vehicle.status == status)
        if is_active is not None:
            stmt = stmt.where(Vehicle.is_active == is_active)
            count_stmt = count_stmt.where(Vehicle.is_active == is_active)

        sort_col = getattr(Vehicle, sort_by, Vehicle.id)
        stmt = stmt.order_by(desc(sort_col) if sort_dir.lower() == "desc" else asc(sort_col))

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total
