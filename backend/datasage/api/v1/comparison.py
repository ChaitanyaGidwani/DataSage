"""Comparison API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import get_session
from datasage.schemas.comparison import ComparisonRequest, ComparisonResponse
from datasage.services.comparison_service import ComparisonService

router = APIRouter()


@router.post("", response_model=ComparisonResponse)
async def compare_properties_post(
    body: ComparisonRequest,
    session: AsyncSession = Depends(get_session),
) -> ComparisonResponse:
    """Compare 2 to 4 properties side-by-side."""
    service = ComparisonService(session)
    return await service.compare_properties(body.property_ids)


@router.get("", response_model=ComparisonResponse)
async def compare_properties_get(
    ids: str = Query(..., description="Comma-separated list of 2 to 4 property UUIDs"),
    session: AsyncSession = Depends(get_session),
) -> ComparisonResponse:
    """Compare properties via comma-separated query param (e.g. ?ids=uuid1,uuid2)."""
    raw_ids = [s.strip() for s in ids.split(",") if s.strip()]
    try:
        parsed_ids = [uuid.UUID(s) for s in raw_ids]
    except ValueError as e:
        from datasage.core.exceptions import ValidationError
        raise ValidationError(f"Invalid property UUID provided: {e}") from e

    service = ComparisonService(session)
    return await service.compare_properties(parsed_ids)
