import httpx

from app.core.config import BOOKING_SERVICE_URL
from app.exceptions import BookingNotFound, BookingServiceUnavailable
from app.schemas.api import BookingResponse


def get_booking(booking_id: int) -> BookingResponse:
    try:
        response = httpx.get(
            f"{BOOKING_SERVICE_URL}/internal/bookings/{booking_id}",
            timeout=5.0,
        )
    except httpx.RequestError as exc:
        raise BookingServiceUnavailable("Booking service is unavailable") from exc

    if response.status_code == 404:
        raise BookingNotFound(f"Booking {booking_id} was not found")
    if response.status_code != 200:
        raise BookingServiceUnavailable(
            f"Booking service returned status {response.status_code}"
        )
    return BookingResponse.model_validate(response.json())


def update_booking_status(booking_id: int, new_status: str) -> None:
    try:
        response = httpx.patch(
            f"{BOOKING_SERVICE_URL}/internal/bookings/{booking_id}/status",
            json={"status": new_status},
            timeout=5.0,
        )
    except httpx.RequestError as exc:
        raise BookingServiceUnavailable("Booking service is unavailable") from exc

    if response.status_code != 200:
        raise BookingServiceUnavailable(
            f"Booking status update failed with status {response.status_code}"
        )


def list_report_bookings(branch_id: int, start_at: str, end_at: str) -> list[dict]:
    try:
        response = httpx.get(
            f"{BOOKING_SERVICE_URL}/internal/reports/bookings",
            params={
                "branch_id": branch_id,
                "start_at": start_at,
                "end_at": end_at,
            },
            timeout=5.0,
        )
    except httpx.RequestError as exc:
        raise BookingServiceUnavailable("Booking service is unavailable") from exc

    if response.status_code != 200:
        raise BookingServiceUnavailable(
            f"Booking report failed with status {response.status_code}"
        )
    return response.json()
