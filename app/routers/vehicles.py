from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleStatusUpdate
from app.schemas.common import PaginatedResponse
from app.services.vehicle_service import VehicleService
from app.core.security import require_role, get_current_user
from app.models.user import User

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    req: VehicleCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("ADMIN")),
):
    return VehicleService.create_vehicle(db, req)


@router.get("", response_model=PaginatedResponse[VehicleResponse])
def list_vehicles(
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    status: Optional[str] = Query(None, description="Filter by status (AVAILABLE, BOOKED, UNDER_MAINTENANCE, RETIRED)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("id", description="Sort by field: id, make, model"),
    sort_dir: str = Query("asc", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
):
    items, total = VehicleService.list_vehicles(
        db=db,
        branch_id=branch_id,
        category_id=category_id,
        status=status,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return PaginatedResponse(items=items, total=total, page=page, size=size)


@router.patch("/{id}/status", response_model=VehicleResponse)
def update_vehicle_status(
    id: int,
    req: VehicleStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _staff=Depends(require_role("BRANCH_STAFF")),
):
    return VehicleService.update_vehicle_status(db, id, req, current_user)
