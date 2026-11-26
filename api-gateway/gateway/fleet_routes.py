from fastapi import APIRouter, Request

from .proxy_utils import forward_request
from .service_addresses import SERVICES

router = APIRouter()
FLEET_SERVICE = SERVICES["vehicles"]


@router.post("/branches", include_in_schema=False)
async def create_branch(request: Request):
    return await forward_request(FLEET_SERVICE, request, "branches")


@router.get("/branches", include_in_schema=False)
async def list_branches(request: Request):
    return await forward_request(FLEET_SERVICE, request, "branches")


@router.get("/branches/{branch_id}", include_in_schema=False)
async def get_branch(branch_id: int, request: Request):
    return await forward_request(
        FLEET_SERVICE, request, f"branches/{branch_id}"
    )


@router.patch("/branches/{branch_id}", include_in_schema=False)
async def update_branch(branch_id: int, request: Request):
    return await forward_request(
        FLEET_SERVICE, request, f"branches/{branch_id}"
    )


@router.post("/vehicles", include_in_schema=False)
async def create_vehicle(request: Request):
    return await forward_request(FLEET_SERVICE, request, "vehicles")


@router.get("/vehicles", include_in_schema=False)
async def list_vehicles(request: Request):
    return await forward_request(FLEET_SERVICE, request, "vehicles")


@router.get("/vehicles/{vehicle_id}", include_in_schema=False)
async def get_vehicle(vehicle_id: int, request: Request):
    return await forward_request(
        FLEET_SERVICE, request, f"vehicles/{vehicle_id}"
    )


@router.patch("/vehicles/{vehicle_id}/status", include_in_schema=False)
async def update_vehicle_status(vehicle_id: int, request: Request):
    path = f"vehicles/{vehicle_id}/status"
    return await forward_request(FLEET_SERVICE, request, path)
