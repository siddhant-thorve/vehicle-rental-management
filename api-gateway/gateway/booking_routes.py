from fastapi import APIRouter, Request

from .proxy_utils import forward_request
from .service_addresses import SERVICES

router = APIRouter()
BOOKING_SERVICE = SERVICES["bookings"]


@router.get("/availability", include_in_schema=False)
async def search_availability(request: Request):
    return await forward_request(BOOKING_SERVICE, request, "availability")


@router.post("/bookings/quote", include_in_schema=False)
async def get_quote(request: Request):
    return await forward_request(BOOKING_SERVICE, request, "bookings/quote")


@router.post("/bookings", include_in_schema=False)
async def create_booking(request: Request):
    return await forward_request(BOOKING_SERVICE, request, "bookings")


@router.get("/bookings/me", include_in_schema=False)
async def list_my_bookings(request: Request):
    return await forward_request(BOOKING_SERVICE, request, "bookings/me")


@router.get("/bookings/branch", include_in_schema=False)
async def list_branch_bookings(request: Request):
    return await forward_request(BOOKING_SERVICE, request, "bookings/branch")


@router.get("/bookings/{booking_id:int}", include_in_schema=False)
async def get_booking(booking_id: int, request: Request):
    return await forward_request(
        BOOKING_SERVICE, request, f"bookings/{booking_id}"
    )


@router.patch("/bookings/{booking_id}/cancel", include_in_schema=False)
async def cancel_booking(booking_id: int, request: Request):
    path = f"bookings/{booking_id}/cancel"
    return await forward_request(BOOKING_SERVICE, request, path)
