from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gateway.auth_routes import router as auth_router
from gateway.booking_routes import router as booking_router
from gateway.catalog_routes import router as catalog_router
from gateway.fleet_routes import router as fleet_router
from gateway.health import router as health_router
from gateway.openapi_docs import create_custom_openapi
from gateway.operations_routes import router as operations_router
from gateway.service_addresses import TAGS_METADATA

app = FastAPI(
    title="Vehicle Rental Management System (Microservices API Gateway)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(fleet_router)
app.include_router(catalog_router)
app.include_router(booking_router)
app.include_router(operations_router)
app.openapi = create_custom_openapi(app)
