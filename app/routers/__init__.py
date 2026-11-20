from app.routers.auth import router as auth_router
from app.routers.customers import router as customers_router
from app.routers.branches import router as branches_router
from app.routers.vehicle_categories import router as categories_router
from app.routers.vehicles import router as vehicles_router
from app.routers.tariffs import router as tariffs_router
from app.routers.availability import router as availability_router
from app.routers.bookings import router as bookings_router
from app.routers.rentals import router as rentals_router
from app.routers.invoices import router as invoices_router
from app.routers.reports import router as reports_router
from app.routers.health import router as health_router

__all__ = [
    "auth_router",
    "customers_router",
    "branches_router",
    "categories_router",
    "vehicles_router",
    "tariffs_router",
    "availability_router",
    "bookings_router",
    "rentals_router",
    "invoices_router",
    "reports_router",
    "health_router",
]
