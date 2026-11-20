from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
import logging

from app.models.tariff import Tariff
from app.schemas.tariff import TariffCreate
from app.repositories.tariff_repo import TariffRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger("tariff_audit")


class TariffService:
    @staticmethod
    def create_tariff(db: Session, req: TariffCreate) -> Tariff:
        category = VehicleRepository.get_category_by_id(db, req.category_id)
        if not category or not category.is_active:
            raise NotFoundException(f"Vehicle Category ID {req.category_id} not found or inactive")

        # Reject negative or zero amounts
        if (
            req.hourly_rate <= 0
            or req.daily_rate <= 0
            or req.weekly_rate <= 0
            or req.extra_km_rate <= 0
            or req.extra_hour_rate <= 0
            or req.deposit_amount <= 0
        ):
            raise BadRequestException("Rates and deposit amounts must be greater than zero")

        effective_from = req.effective_from or datetime.now(timezone.utc)
        if effective_from.tzinfo is None:
            effective_from = effective_from.replace(tzinfo=timezone.utc)

        tariff = Tariff(
            category_id=req.category_id,
            hourly_rate=req.hourly_rate,
            daily_rate=req.daily_rate,
            weekly_rate=req.weekly_rate,
            free_km_per_day=req.free_km_per_day,
            extra_km_rate=req.extra_km_rate,
            extra_hour_rate=req.extra_hour_rate,
            deposit_amount=req.deposit_amount,
            effective_from=effective_from,
            is_active=True,
        )
        created = TariffRepository.create(db, tariff)
        logger.info(f"AUDIT: Tariff created ID {created.id} for Category ID {req.category_id}")
        return created

    @staticmethod
    def list_tariffs(
        db: Session,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Tariff], int]:
        skip = (page - 1) * size
        return TariffRepository.list_tariffs(
            db=db,
            category_id=category_id,
            is_active=is_active,
            skip=skip,
            limit=size,
        )

    @staticmethod
    def get_active_tariff(db: Session, category_id: int) -> Tariff:
        tariff = TariffRepository.get_active_by_category(db, category_id)
        if not tariff:
            raise NotFoundException(f"No active tariff found for Category ID {category_id}")
        return tariff
