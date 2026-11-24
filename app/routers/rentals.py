from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.rental import PickupRequest, ReturnRequest, RentalResponse
from app.schemas.invoice import InvoiceResponse
from app.services.rental_service import RentalService
from app.core.security import require_role
from app.models.user import User

router = APIRouter(prefix="/rentals", tags=["Rental Lifecycle"])


@router.post("/{booking_id}/pickup", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def record_pickup(
    booking_id: int,
    req: PickupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("BRANCH_STAFF")),
):
    return RentalService.record_pickup(db, booking_id, req, current_user)


@router.post("/{booking_id}/return", response_model=InvoiceResponse, status_code=status.HTTP_200_OK)
def record_return(
    booking_id: int,
    req: ReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("BRANCH_STAFF")),
):
    return RentalService.record_return(db, booking_id, req, current_user)
