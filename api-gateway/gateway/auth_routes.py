from fastapi import APIRouter, Request

from .proxy_utils import forward_request
from .service_addresses import SERVICES

router = APIRouter()
AUTH_SERVICE = SERVICES["auth"]


@router.post("/auth/register", include_in_schema=False)
async def register(request: Request):
    return await forward_request(AUTH_SERVICE, request, "auth/register")


@router.post("/auth/login", include_in_schema=False)
async def login(request: Request):
    return await forward_request(AUTH_SERVICE, request, "auth/login")


@router.post("/auth/staff", include_in_schema=False)
async def create_staff(request: Request):
    return await forward_request(AUTH_SERVICE, request, "auth/staff")


@router.patch("/customers/{customer_id}/verify-licence", include_in_schema=False)
async def verify_customer_licence(customer_id: int, request: Request):
    path = f"customers/{customer_id}/verify-licence"
    return await forward_request(AUTH_SERVICE, request, path)


@router.get("/customers/{customer_id}", include_in_schema=False)
async def get_customer(customer_id: int, request: Request):
    return await forward_request(
        AUTH_SERVICE, request, f"customers/{customer_id}"
    )
