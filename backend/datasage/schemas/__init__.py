"""Common schemas: pagination, error response, health."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class CursorPagination(BaseModel):
    """Cursor-based pagination metadata."""

    next_cursor: str | None = None
    has_more: bool = False
    total_count: int = 0


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response wrapper."""

    data: list[T]
    pagination: CursorPagination


class ErrorDetail(BaseModel):
    """Structured error response."""

    code: str
    message: str
    request_id: str = ""
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Top-level error wrapper."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    env: str
