"""Valuation API endpoints — AI price prediction."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.api.deps import get_current_user, require_role
from datasage.core.database import get_session
from datasage.models.user import User
from datasage.services.valuation_service import ValuationService

router = APIRouter()


@router.get("/{property_id}")
async def get_valuation(
    property_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Get AI valuation for a specific property."""
    service = ValuationService(session)
    return await service.predict_value(property_id)


@router.post("/bulk")
async def bulk_valuations(
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Generate valuations for all unvalued properties (admin only)."""
    service = ValuationService(session)
    predictions = await service.bulk_predict(limit=limit)
    return {"generated": len(predictions), "predictions": predictions}
