import httpx
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from .health import health
from .service_addresses import TAGS_METADATA

SERVICE_PORTS = [8001, 8002, 8003, 8004, 8005]


def create_custom_openapi(app: FastAPI):
    """Combine the service API descriptions for the gateway's Swagger page."""
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        paths = {}
        schemas = {}

        with httpx.Client(timeout=3.0) as client:
            for port in SERVICE_PORTS:
                try:
                    response = client.get(
                        f"http://127.0.0.1:{port}/openapi.json"
                    )
                    if response.status_code != 200:
                        continue

                    service_docs = response.json()
                    for path, details in service_docs.get("paths", {}).items():
                        if path == "/health" or path.startswith("/internal"):
                            continue

                        for operation in details.values():
                            if (
                                isinstance(operation, dict)
                                and operation.get("summary", "").startswith("[")
                            ):
                                operation["security"] = [
                                    {"OAuth2PasswordBearer": []}
                                ]
                        paths[path] = details

                    schemas.update(
                        service_docs.get("components", {}).get("schemas", {})
                    )
                except (httpx.RequestError, ValueError):
                    continue

        health_route = APIRoute(
            "/health",
            health,
            methods=["GET"],
            tags=["Health"],
            summary="Health Check",
        )
        health_docs = get_openapi(
            title="Health", version="1.0.0", routes=[health_route]
        )
        if "/health" in health_docs.get("paths", {}):
            paths["/health"] = health_docs["paths"]["/health"]

        app.openapi_schema = {
            "openapi": "3.1.0",
            "info": {
                "title": "Vehicle Rental Management System (Microservices)",
                "version": "1.0.0",
                "description": (
                    "Unified API Gateway for Auth, Fleet, Catalog, Booking, "
                    "and Rental Operations. Click 'Authorize' to log in."
                ),
            },
            "tags": TAGS_METADATA,
            "paths": paths,
            "components": {
                "schemas": schemas,
                "securitySchemes": {
                    "OAuth2PasswordBearer": {
                        "type": "oauth2",
                        "description": (
                            "Enter your login credentials (username/password) "
                            "or ******"
                        ),
                        "flows": {
                            "password": {
                                "tokenUrl": "/auth/login",
                                "scopes": {},
                            }
                        },
                    }
                },
            },
        }
        return app.openapi_schema

    return custom_openapi
