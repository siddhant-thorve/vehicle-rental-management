from app.routers.customers import router as customers_router
from app.routers.branches import router as branches_router
from app.routers.vehicle_categories import router as categories_router
from app.routers.vehicles import router as vehicles_router
from app.routers.tariffs import router as tariffs_router
from app.routers.health import router as health_router

__all__ = [
    "customers_router",
    "branches_router",
    "categories_router",
    "vehicles_router",
    "tariffs_router",
    "health_router",
]
