class BookingServiceUnavailable(Exception):
    """Raised when the booking service cannot be reached."""


class BookingNotFound(Exception):
    """Raised when a requested booking does not exist."""
