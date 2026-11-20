import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.exceptions import AppException
from app.routers import (
    auth_router,
    customers_router,
    branches_router,
    categories_router,
    vehicles_router,
    tariffs_router,
    availability_router,
    bookings_router,
    rentals_router,
    invoices_router,
    reports_router,
    health_router,
)

# Configure structured audit logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Vehicle Rental Management System REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Format readable error message
    error_msg = "; ".join([f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in errors])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": error_msg, "code": "VALIDATION_ERROR"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred.", "code": "INTERNAL_SERVER_ERROR"},
    )


# Router registrations
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(branches_router)
app.include_router(categories_router)
app.include_router(vehicles_router)
app.include_router(tariffs_router)
app.include_router(availability_router)
app.include_router(bookings_router)
app.include_router(rentals_router)
app.include_router(invoices_router)
app.include_router(reports_router)


@app.get("/", include_in_schema=False)
def root():
    return {
        "project": settings.PROJECT_NAME,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
