# Backend URLs used by the gateway routes.
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

SERVICE_HEALTH_URLS = {
    "auth-service": "http://127.0.0.1:8001/health",
    "fleet-service": "http://127.0.0.1:8002/health",
    "catalog-service": "http://127.0.0.1:8005/health",
    "booking-service": "http://127.0.0.1:8003/health",
    "rental-operations-service": "http://127.0.0.1:8004/health",
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
