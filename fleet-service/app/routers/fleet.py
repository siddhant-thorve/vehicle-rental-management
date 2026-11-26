from typing import Optional, List
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.config import CATALOG_SERVICE_URL
from app.core.security import CurrentUser, require_role
from app.db.session import get_db
from app.models.entities import Branch, Vehicle
from app.repositories import fleet as repositories
from app.schemas.api import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    VehicleCreate,
    VehicleStatusUpdate,
    VehicleResponse,
)

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health Check")
def health():
    return {"status": "ok", "service": "fleet-service"}


# ==================== BRANCHES ====================

@router.post("/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED, tags=["Branches"], summary="[ADMIN] Create Branch")
def create_branch(
    req: BranchCreate,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_role(["ADMIN"])),
):
    branch = Branch(
        name=req.name,
        city=req.city,
        address=req.address,
        contact_no=req.contact_no,
        is_active=True,
    )
    return repositories.create_branch(db, branch)


@router.get("/branches", response_model=List[BranchResponse], tags=["Branches"], summary="List Branches")
def list_branches(
    city: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return repositories.list_branches(db, city, page, size)


@router.get("/branches/{branch_id}", response_model=BranchResponse, tags=["Branches"], summary="Get Branch Details")
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = repositories.get_branch(db, branch_id, active_only=True)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    return branch


@router.patch("/branches/{branch_id}", response_model=BranchResponse, tags=["Branches"], summary="[ADMIN] Update Branch")
def update_branch(
    branch_id: int,
    req: BranchUpdate,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_role(["ADMIN"])),
):
    branch = repositories.get_branch(db, branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    return repositories.update_branch(db, branch, req.address, req.contact_no)


# ==================== VEHICLES ====================

@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED, tags=["Vehicles"], summary="[ADMIN] Register New Vehicle")
def create_vehicle(
    req: VehicleCreate,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_role(["ADMIN"])),
):
    existing = repositories.get_vehicle_by_registration(db, req.registration_no)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration number already registered")

    branch = repositories.get_branch(db, req.branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

    try:
        category_response = httpx.get(
            f"{CATALOG_SERVICE_URL}/vehicle-categories/{req.category_id}",
            timeout=5.0,
        )
        if category_response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        category_response.raise_for_status()
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Catalog service unavailable: {exc}",
        ) from exc

    vehicle = Vehicle(
        registration_no=req.registration_no,
        category_id=req.category_id,
        branch_id=req.branch_id,
        make=req.make,
        model=req.model,
        fuel_type=req.fuel_type,
        transmission=req.transmission,
        odometer_km=req.odometer_km,
        status="AVAILABLE",
        is_active=True,
    )
    return repositories.create_vehicle(db, vehicle)


@router.get("/vehicles", response_model=List[VehicleResponse], tags=["Vehicles"], summary="List and Filter Fleet")
def list_vehicles(
    branch_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return repositories.list_vehicles(db, branch_id, category_id, status, page, size)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse, tags=["Vehicles"], summary="Get Vehicle Details")
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = repositories.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


@router.patch("/vehicles/{vehicle_id}/status", response_model=VehicleResponse, tags=["Vehicles"], summary="[BRANCH_STAFF / ADMIN] Update Vehicle Status")
def update_vehicle_status(
    vehicle_id: int,
    req: VehicleStatusUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role(["ADMIN", "BRANCH_STAFF"])),
):
    vehicle = repositories.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    if user.role == "BRANCH_STAFF" and user.branch_id != vehicle.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify vehicle of another branch")

    return repositories.update_vehicle_status(db, vehicle, req.status, req.odometer_km)


@router.patch("/internal/vehicles/{vehicle_id}/status", response_model=VehicleResponse, include_in_schema=False)
def update_vehicle_status_internal(
    vehicle_id: int,
    req: VehicleStatusUpdate,
    db: Session = Depends(get_db),
):
    vehicle = repositories.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return repositories.update_vehicle_status(db, vehicle, req.status, req.odometer_km)
