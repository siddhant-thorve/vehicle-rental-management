from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoice import InvoiceResponse
from app.services.rental_service import RentalService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("/{rental_id}", response_model=InvoiceResponse)
def get_invoice(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RentalService.get_invoice_by_rental_id(db, rental_id, current_user)
