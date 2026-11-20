from typing import Optional, Any


class AppException(Exception):
    def __init__(self, message: str, code: str = "BAD_REQUEST", status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message=message, code=code, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict detected", code: str = "CONFLICT"):
        super().__init__(message=message, code=code, status_code=409)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request", code: str = "BAD_REQUEST"):
        super().__init__(message=message, code=code, status_code=400)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", code: str = "VALIDATION_ERROR", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=422, details=details)
