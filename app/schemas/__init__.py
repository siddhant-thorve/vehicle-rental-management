from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.user import (
    UserRole,
    CustomerRegisterRequest,
    StaffCreateRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserListResponse,
)
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse
from app.schemas.vehicle import (
    VehicleStatus,
    CategoryCreate,
    CategoryResponse,
    VehicleCreate,
    VehicleStatusUpdate,
    VehicleResponse,
)
from app.schemas.tariff import TariffCreate, TariffResponse
from app.schemas.booking import (
    BookingStatus,
    QuoteRequest,
    QuoteResponse,
    BookingCreate,
    BookingResponse,
    CancelResponse,
)
from app.schemas.rental import PickupRequest, ReturnRequest, RentalResponse
from app.schemas.invoice import InvoiceResponse
from app.schemas.report import UtilisationReportResponse, RevenueReportResponse

__all__ = [
    "PaginatedResponse",
    "MessageResponse",
    "UserRole",
    "CustomerRegisterRequest",
    "StaffCreateRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    "UserListResponse",
    "BranchCreate",
    "BranchUpdate",
    "BranchResponse",
    "VehicleStatus",
    "CategoryCreate",
    "CategoryResponse",
    "VehicleCreate",
    "VehicleStatusUpdate",
    "VehicleResponse",
    "TariffCreate",
    "TariffResponse",
    "BookingStatus",
    "QuoteRequest",
    "QuoteResponse",
    "BookingCreate",
    "BookingResponse",
    "CancelResponse",
    "PickupRequest",
    "ReturnRequest",
    "RentalResponse",
    "InvoiceResponse",
    "UtilisationReportResponse",
    "RevenueReportResponse",
]
