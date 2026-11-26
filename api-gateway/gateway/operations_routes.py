from fastapi import APIRouter, Request

from .proxy_utils import forward_request
from .service_addresses import SERVICES

router = APIRouter()
OPERATIONS_SERVICE = SERVICES["rentals"]


@router.post("/rentals/{booking_id}/pickup", include_in_schema=False)
async def record_pickup(booking_id: int, request: Request):
    path = f"rentals/{booking_id}/pickup"
    return await forward_request(OPERATIONS_SERVICE, request, path)


@router.post("/rentals/{booking_id}/return", include_in_schema=False)
async def return_vehicle(booking_id: int, request: Request):
    path = f"rentals/{booking_id}/return"
    return await forward_request(OPERATIONS_SERVICE, request, path)


@router.get("/invoices/{rental_id}", include_in_schema=False)
async def get_invoice(rental_id: int, request: Request):
    return await forward_request(
        OPERATIONS_SERVICE, request, f"invoices/{rental_id}"
    )


@router.get("/reports/utilisation", include_in_schema=False)
async def get_utilisation_report(request: Request):
    return await forward_request(
        OPERATIONS_SERVICE, request, "reports/utilisation"
    )


@router.get("/reports/revenue", include_in_schema=False)
async def get_revenue_report(request: Request):
    return await forward_request(
        OPERATIONS_SERVICE, request, "reports/revenue"
    )
