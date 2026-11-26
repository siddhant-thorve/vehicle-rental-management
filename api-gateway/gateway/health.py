import httpx
from fastapi import APIRouter

from .service_addresses import SERVICE_HEALTH_URLS

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health Check")
async def health():
    """Check if the gateway and each microservice are responding."""
    statuses = {}

    async with httpx.AsyncClient(timeout=3.0) as client:
        for service_name, health_url in SERVICE_HEALTH_URLS.items():
            try:
                response = await client.get(health_url)
                statuses[service_name] = (
                    "ok" if response.status_code == 200
                    else f"error ({response.status_code})"
                )
            except httpx.RequestError:
                statuses[service_name] = "offline"

    return {"gateway": "ok", "services": statuses}
