from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tariff import TariffCreate, TariffResponse
from app.schemas.common import PaginatedResponse
from app.services.tariff_service import TariffService

router = APIRouter(prefix="/tariffs", tags=["Tariffs & Pricing"])


@router.post("", response_model=TariffResponse, status_code=status.HTTP_201_CREATED)
def create_tariff(
    req: TariffCreate,
    db: Session = Depends(get_db),
):
    return TariffService.create_tariff(db, req)


@router.get("", response_model=PaginatedResponse[TariffResponse])
def list_tariffs(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_active: Optional[bool] = Query(None, description="Filter active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
):
    items, total = TariffService.list_tariffs(
        db=db,
        category_id=category_id,
        is_active=is_active,
        page=page,
        size=size,
    )
    return PaginatedResponse(items=items, total=total, page=page, size=size)
