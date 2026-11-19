from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    BRANCH_STAFF = "BRANCH_STAFF"
    CUSTOMER = "CUSTOMER"


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    RETIRED = "RETIRED"


class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class FuelType(str, Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    ELECTRIC = "ELECTRIC"


class TransmissionType(str, Enum):
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"