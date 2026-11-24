from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.core.security import require_role

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.patch("/{id}/verify-licence", response_model=UserResponse)
def verify_customer_licence(
    id: int,
    db: Session = Depends(get_db),
    _staff=Depends(require_role("BRANCH_STAFF")),
):
    return AuthService.verify_licence(db, customer_id=id)
