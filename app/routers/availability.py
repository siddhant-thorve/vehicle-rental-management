from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.vehicle import VehicleResponse
from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/availability", tags=["Availability"])


@router.get("", response_model=List[VehicleResponse])
def search_availability(
    branch_id: int = Query(..., description="Branch ID where pickup takes place"),
    pickup_at: datetime = Query(..., description="Requested pickup date-time (ISO format)"),
    drop_at: datetime = Query(..., description="Requested drop-off date-time (ISO format)"),
    category_id: Optional[int] = Query(None, description="Optional vehicle category ID filter"),
    db: Session = Depends(get_db),
):
    return VehicleService.search_available_vehicles(
        db=db,
        branch_id=branch_id,
        pickup_at=pickup_at,
        drop_at=drop_at,
        category_id=category_id,
    )
