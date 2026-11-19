"""Custom exception hierarchy for structured error handling.

See docs/21-error-handling.md for the full error taxonomy.
"""

from __future__ import annotations

from typing import Any


class DataSageError(Exception):
    """Base exception for all DataSage application errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(DataSageError):
    """Resource not found (404)."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource} not found",
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class ValidationError(DataSageError):
    """Input validation failure (422)."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details={"field": field} if field else {},
        )


class AuthenticationError(DataSageError):
    """Authentication failure (401)."""

    def __init__(self, message: str = "Invalid credentials", code: str = "AUTH_INVALID_CREDENTIALS") -> None:
        super().__init__(message=message, code=code, status_code=401)


class AuthorizationError(DataSageError):
    """Authorization failure (403)."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


class ConflictError(DataSageError):
    """Resource conflict (409)."""

    def __init__(self, message: str, code: str = "CONFLICT") -> None:
        super().__init__(message=message, code=code, status_code=409)


class AccountLockedError(DataSageError):
    """Account locked due to too many failed login attempts (423)."""

    def __init__(self, retry_after_minutes: int = 15) -> None:
        super().__init__(
            message=f"Account locked. Try again in {retry_after_minutes} minutes.",
            code="AUTH_ACCOUNT_LOCKED",
            status_code=423,
            details={"retry_after_minutes": retry_after_minutes},
        )


class RateLimitError(DataSageError):
    """Rate limit exceeded (429)."""

    def __init__(self, retry_after: int) -> None:
        super().__init__(
            message=f"Too many requests. Please try again in {retry_after} seconds.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after},
        )


class InsufficientDataError(DataSageError):
    """Not enough data for ML prediction (422)."""

    def __init__(self, missing_fields: list[str]) -> None:
        super().__init__(
            message=f"Insufficient data for prediction. Missing: {', '.join(missing_fields)}",
            code="INSUFFICIENT_DATA",
            status_code=422,
            details={"missing_fields": missing_fields},
        )


class ModelNotLoadedError(DataSageError):
    """ML model is not available (503)."""

    def __init__(self) -> None:
        super().__init__(
            message="AI analysis is temporarily unavailable.",
            code="MODEL_NOT_LOADED",
            status_code=503,
        )


class ServiceUnavailableError(DataSageError):
    """External service is down (503)."""

    def __init__(self, service: str = "Service") -> None:
        super().__init__(
            message=f"{service} is temporarily unavailable.",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )
