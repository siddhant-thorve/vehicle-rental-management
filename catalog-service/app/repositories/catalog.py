from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.models.entities import Tariff, VehicleCategory


def create_category(db: Session, category: VehicleCategory) -> VehicleCategory:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category_by_name(db: Session, name: str) -> VehicleCategory | None:
    return db.query(VehicleCategory).filter(VehicleCategory.name == name).first()


def list_categories(db: Session) -> list[VehicleCategory]:
    return db.query(VehicleCategory).filter(VehicleCategory.is_active.is_(True)).all()


def get_category(db: Session, category_id: int) -> VehicleCategory | None:
    return db.query(VehicleCategory).filter(VehicleCategory.id == category_id).first()


def create_tariff(db: Session, tariff: Tariff) -> Tariff:
    db.add(tariff)
    db.commit()
    db.refresh(tariff)
    return tariff


def list_tariffs(
    db: Session, category_id: Optional[int]
) -> list[Tariff]:
    query = db.query(Tariff)
    if category_id is not None:
        query = query.filter(Tariff.category_id == category_id)
    return query.order_by(Tariff.id.desc()).all()


def get_latest_tariff(db: Session, category_id: int) -> Tariff | None:
    return (
        db.query(Tariff)
        .filter(Tariff.category_id == category_id)
        .order_by(Tariff.id.desc())
        .first()
    )


def seed_records_if_empty(db: Session, records: Sequence[object]) -> bool:
    if not records:
        return False
    model = type(records[0])
    if db.query(model).first():
        return False
    db.add_all(records)
    db.commit()
    return True
