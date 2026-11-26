import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi


app = FastAPI(
    title="Vehicle Rental Management System (Microservices API Gateway)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "auth": "http://127.0.0.1:8001",
    "customers": "http://127.0.0.1:8001",
    "branches": "http://127.0.0.1:8002",
    "vehicle-categories": "http://127.0.0.1:8005",
    "vehicles": "http://127.0.0.1:8002",
    "tariffs": "http://127.0.0.1:8005",
    "availability": "http://127.0.0.1:8003",
    "bookings": "http://127.0.0.1:8003",
    "rentals": "http://127.0.0.1:8004",
    "invoices": "http://127.0.0.1:8004",
    "reports": "http://127.0.0.1:8004",
}

TAGS_METADATA = [
    {"name": "Authentication", "description": "User registration, login, and staff management"},
    {"name": "Customers", "description": "Customer driving licence verification & profile"},
    {"name": "Branches", "description": "Rental branch management"},
    {"name": "Vehicle Categories", "description": "Vehicle category classification"},
    {"name": "Vehicles", "description": "Fleet management & status tracking"},
    {"name": "Tariffs & Pricing", "description": "Rate cards, free-km, and security deposit"},
    {"name": "Availability", "description": "Conflict-free vehicle search"},
    {"name": "Bookings", "description": "Booking creation, quotes, and cancellation policy"},
    {"name": "Rental Lifecycle", "description": "Vehicle pickup, return & settlement"},
    {"name": "Invoices", "description": "Settlement & billing invoices"},
    {"name": "Reporting & Analytics", "description": "Fleet utilisation & revenue reports"},
    {"name": "Health", "description": "System health checks"},
]


@app.get("/health", tags=["Health"], summary="Health Check")
async def health():
    """Aggregated health check across all microservices"""
    results = {"gateway": "ok", "services": {}}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, port in [
            ("auth-service", 8001),
            ("fleet-service", 8002),
            ("catalog-service", 8005),
            ("booking-service", 8003),
            ("rental-operations-service", 8004),
        ]:
            try:
                res = await client.get(f"http://127.0.0.1:{port}/health")
                results["services"][name] = "ok" if res.status_code == 200 else f"error ({res.status_code})"
            except Exception:
                results["services"][name] = "offline"
    return results


def custom_openapi():
    """Merge OpenAPI documentation from all microservices into one unified Swagger UI"""
    if app.openapi_schema:
        return app.openapi_schema

    merged_paths = {}
    merged_components = {"schemas": {}}

    with httpx.Client(timeout=3.0) as client:
        for port in [8001, 8002, 8003, 8004, 8005]:
            try:
                res = client.get(f"http://127.0.0.1:{port}/openapi.json")
                if res.status_code == 200:
                    spec = res.json()
                    for path, path_item in spec.get("paths", {}).items():
                        if path != "/health" and not path.startswith("/internal"):
                            # Attach lock / security to any endpoint requiring specific role
                            for method, operation in path_item.items():
                                if isinstance(operation, dict):
                                    summary = operation.get("summary", "")
                                    if summary.startswith("["):
                                        operation["security"] = [{"OAuth2PasswordBearer": []}]
                            merged_paths[path] = path_item
                    schemas = spec.get("components", {}).get("schemas", {})
                    merged_components["schemas"].update(schemas)
            except Exception:
                pass

    # Add health check endpoint
    health_spec = get_openapi(title="Health", version="1.0.0", routes=[r for r in app.routes if r.path == "/health"])
    if "/health" in health_spec.get("paths", {}):
        merged_paths["/health"] = health_spec["paths"]["/health"]

    # Configure OAuth2PasswordBearer Security Scheme so Swagger displays the Authorize button
    merged_components["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "description": "Enter your login credentials (username/password) or Bearer token",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {}
                }
            }
        }
    }

    app.openapi_schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Vehicle Rental Management System (Microservices)",
            "version": "1.0.0",
            "description": "Unified API Gateway for Auth, Fleet, Catalog, Booking, and Rental Operations. Click 'Authorize' to log in.",
        },
        "tags": TAGS_METADATA,
        "paths": merged_paths,
        "components": merged_components,
    }
    return app.openapi_schema

app.openapi = custom_openapi


# Forwarding logic for all endpoints
async def forward_request(target_base: str, request: Request, subpath: str = ""):
    url = f"{target_base}/{subpath}" if subpath else target_base
    if request.url.query:
        url = f"{url}?{request.url.query}"

    body = await request.body()
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ["host", "content-length"]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type"),
            )
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=503,
            content={"detail": f"Service unavailable: {str(exc)}", "code": "SERVICE_UNAVAILABLE"},
        )


@app.api_route("/{prefix}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
@app.api_route("/{prefix}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def route_traffic(prefix: str, request: Request, path: str = ""):
    target_service = SERVICES.get(prefix)
    if not target_service:
        return JSONResponse(status_code=404, content={"detail": f"No service mapped for /{prefix}"})
    
    full_subpath = f"{prefix}/{path}" if path else prefix
    return await forward_request(target_service, request, full_subpath)
