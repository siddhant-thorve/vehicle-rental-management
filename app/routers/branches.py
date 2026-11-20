from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.branch import BranchCreate, BranchResponse
from app.schemas.common import PaginatedResponse
from app.services.branch_service import BranchService

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(
    req: BranchCreate,
    db: Session = Depends(get_db),
):
    return BranchService.create_branch(db, req)


@router.get("", response_model=PaginatedResponse[BranchResponse])
def list_branches(
    city: Optional[str] = Query(None, description="Filter by city name"),
    is_active: Optional[bool] = Query(None, description="Filter active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("id", description="Sort by field: id, name, city"),
    sort_dir: str = Query("asc", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
):
    items, total = BranchService.list_branches(
        db=db,
        city=city,
        is_active=is_active,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return PaginatedResponse(items=items, total=total, page=page, size=size)
