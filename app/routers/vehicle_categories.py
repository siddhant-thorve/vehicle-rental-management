from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.vehicle import CategoryCreate, CategoryResponse
from app.schemas.common import PaginatedResponse
from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicle-categories", tags=["Vehicle Categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    req: CategoryCreate,
    db: Session = Depends(get_db),
):
    return VehicleService.create_category(db, req)


@router.get("", response_model=PaginatedResponse[CategoryResponse])
def list_categories(
    is_active: Optional[bool] = Query(None, description="Filter active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    sort_by: str = Query("id", description="Sort by field: id, name"),
    sort_dir: str = Query("asc", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
):
    items, total = VehicleService.list_categories(
        db=db,
        is_active=is_active,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return PaginatedResponse(items=items, total=total, page=page, size=size)
