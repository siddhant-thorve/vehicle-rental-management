from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, require_role
from app.db.session import get_db
from app.models.entities import Tariff, VehicleCategory
from app.repositories import catalog as repositories
from app.schemas.api import (
    CategoryCreate,
    CategoryResponse,
    TariffCreate,
    TariffResponse,
)

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health Check")
def health():
    return {"status": "ok", "service": "catalog-service"}


@router.post(
    "/vehicle-categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Vehicle Categories"],
    summary="[ADMIN] Create Vehicle Category",
)
def create_category(
    req: CategoryCreate,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_role(["ADMIN"])),
):
    if repositories.get_category_by_name(db, req.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists",
        )
    category = VehicleCategory(
        name=req.name,
        description=req.description,
        seating_capacity=req.seating_capacity,
        is_active=True,
    )
    return repositories.create_category(db, category)


@router.get(
    "/vehicle-categories",
    response_model=List[CategoryResponse],
    tags=["Vehicle Categories"],
    summary="List Vehicle Categories",
)
def list_categories(db: Session = Depends(get_db)):
    return repositories.list_categories(db)


@router.get(
    "/vehicle-categories/{category_id}",
    response_model=CategoryResponse,
    tags=["Vehicle Categories"],
    summary="Get Category Details",
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = repositories.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@router.post(
    "/tariffs",
    response_model=TariffResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tariffs & Pricing"],
    summary="[ADMIN] Define Tariff Rates",
)
def create_tariff(
    req: TariffCreate,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_role(["ADMIN"])),
):
    if not repositories.get_category(db, req.category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    tariff = Tariff(**req.model_dump())
    return repositories.create_tariff(db, tariff)


@router.get(
    "/tariffs",
    response_model=List[TariffResponse],
    tags=["Tariffs & Pricing"],
    summary="List Category Tariffs",
)
def list_tariffs(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return repositories.list_tariffs(db, category_id)


@router.get(
    "/tariffs/category/{category_id}",
    response_model=TariffResponse,
    tags=["Tariffs & Pricing"],
    summary="Get Tariff for Category",
)
def get_tariff_for_category(category_id: int, db: Session = Depends(get_db)):
    tariff = repositories.get_latest_tariff(db, category_id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff not found for category",
        )
    return tariff
