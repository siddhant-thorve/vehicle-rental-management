from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from datetime import datetime, timezone
from app.models.tariff import Tariff


class TariffRepository:
    @staticmethod
    def get_by_id(db: Session, tariff_id: int) -> Optional[Tariff]:
        return db.get(Tariff, tariff_id)

    @staticmethod
    def get_active_by_category(db: Session, category_id: int) -> Optional[Tariff]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Tariff)
            .where(
                Tariff.category_id == category_id,
                Tariff.is_active.is_(True),
                Tariff.effective_from <= now,
            )
            .order_by(desc(Tariff.effective_from), desc(Tariff.id))
        )
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, tariff: Tariff) -> Tariff:
        db.add(tariff)
        db.commit()
        db.refresh(tariff)
        return tariff

    @staticmethod
    def list_tariffs(
        db: Session,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Tariff], int]:
        stmt = select(Tariff)
        count_stmt = select(func.count(Tariff.id))

        if category_id:
            stmt = stmt.where(Tariff.category_id == category_id)
            count_stmt = count_stmt.where(Tariff.category_id == category_id)
        if is_active is not None:
            stmt = stmt.where(Tariff.is_active == is_active)
            count_stmt = count_stmt.where(Tariff.is_active == is_active)

        stmt = stmt.order_by(desc(Tariff.effective_from))
        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total
