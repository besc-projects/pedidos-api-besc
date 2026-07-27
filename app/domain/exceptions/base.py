"""Application exception hierarchy with standardized HTTP semantics."""


class AppException(Exception):
    """Base application exception. Maps to an HTTP status code."""

    status_code: int = 500
    default_message: str = "Internal server error."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class ValidationException(AppException):
    """Raised when input data violates a domain invariant."""

    status_code = 400
    default_message = "Invalid data provided."


class BusinessException(AppException):
    """Raised when a business rule prevents the operation."""

    status_code = 400
    default_message = "Operation not allowed by business rules."


class UnauthorizedException(AppException):
    """Raised when authentication is missing or invalid."""

    status_code = 401
    default_message = "Unauthorized."


class ForbiddenException(AppException):
    """Raised when the caller lacks permission for the operation."""

    status_code = 403
    default_message = "Forbidden."


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    status_code = 404
    default_message = "Resource not found."


class ConflictException(AppException):
    """Raised when the operation conflicts with the current state."""

    status_code = 409
    default_message = "Resource conflict."
