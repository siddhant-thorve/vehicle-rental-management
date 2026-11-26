from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models.entities import Branch, Vehicle


def create_branch(db: Session, branch: Branch) -> Branch:
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


def list_branches(
    db: Session, city: Optional[str], page: int, size: int
) -> list[Branch]:
    query = db.query(Branch).filter(Branch.is_active.is_(True))
    if city:
        query = query.filter(Branch.city.ilike(f"%{city}%"))
    return query.offset((page - 1) * size).limit(size).all()


def get_branch(db: Session, branch_id: int, active_only: bool = False) -> Branch | None:
    query = db.query(Branch).filter(Branch.id == branch_id)
    if active_only:
        query = query.filter(Branch.is_active.is_(True))
    return query.first()


def update_branch(
    db: Session,
    branch: Branch,
    address: Optional[str],
    contact_no: Optional[str],
) -> Branch:
    if address:
        branch.address = address
    if contact_no:
        branch.contact_no = contact_no
    db.commit()
    db.refresh(branch)
    return branch


def create_vehicle(db: Session, vehicle: Vehicle) -> Vehicle:
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_vehicle_by_registration(db: Session, registration_no: str) -> Vehicle | None:
    return (
        db.query(Vehicle)
        .filter(Vehicle.registration_no == registration_no)
        .first()
    )


def list_vehicles(
    db: Session,
    branch_id: Optional[int],
    category_id: Optional[int],
    vehicle_status: Optional[str],
    page: int,
    size: int,
) -> list[Vehicle]:
    query = db.query(Vehicle).filter(Vehicle.is_active.is_(True))
    if branch_id:
        query = query.filter(Vehicle.branch_id == branch_id)
    if category_id:
        query = query.filter(Vehicle.category_id == category_id)
    if vehicle_status:
        query = query.filter(Vehicle.status == vehicle_status)
    return query.offset((page - 1) * size).limit(size).all()


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def update_vehicle_status(
    db: Session,
    vehicle: Vehicle,
    vehicle_status: str,
    odometer_km: Optional[float],
) -> Vehicle:
    vehicle.status = vehicle_status
    if odometer_km is not None:
        vehicle.odometer_km = odometer_km
    db.commit()
    db.refresh(vehicle)
    return vehicle


def seed_records_if_empty(db: Session, records: Sequence[object]) -> bool:
    if not records:
        return False
    model = type(records[0])
    if db.query(model).first():
        return False
    db.add_all(records)
    db.commit()
    return True
