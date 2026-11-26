from fastapi import APIRouter, Request

from .proxy_utils import forward_request
from .service_addresses import SERVICES

router = APIRouter()
CATALOG_SERVICE = SERVICES["vehicle-categories"]


@router.post("/vehicle-categories", include_in_schema=False)
async def create_category(request: Request):
    return await forward_request(
        CATALOG_SERVICE, request, "vehicle-categories"
    )


@router.get("/vehicle-categories", include_in_schema=False)
async def list_categories(request: Request):
    return await forward_request(
        CATALOG_SERVICE, request, "vehicle-categories"
    )


@router.get("/vehicle-categories/{category_id}", include_in_schema=False)
async def get_category(category_id: int, request: Request):
    path = f"vehicle-categories/{category_id}"
    return await forward_request(CATALOG_SERVICE, request, path)


@router.post("/tariffs", include_in_schema=False)
async def create_tariff(request: Request):
    return await forward_request(CATALOG_SERVICE, request, "tariffs")


@router.get("/tariffs", include_in_schema=False)
async def list_tariffs(request: Request):
    return await forward_request(CATALOG_SERVICE, request, "tariffs")


@router.get("/tariffs/category/{category_id}", include_in_schema=False)
async def get_category_tariff(category_id: int, request: Request):
    path = f"tariffs/category/{category_id}"
    return await forward_request(CATALOG_SERVICE, request, path)
