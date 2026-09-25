"""Admin API endpoints for system metrics, dataset monitoring, and maintenance."""

from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import get_session
from datasage.api.deps import require_role
from datasage.models.user import User
from datasage.models.property import Property
from datasage.models.reference import Locality, City
from datasage.models.valuation import ValuationPrediction
from datasage.services.valuation_service import ValuationService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Get system stats: total properties, valuations, localities, and users."""
    prop_count_res = await session.execute(
        select(func.count()).select_from(Property).where(Property.deleted_at.is_(None))
    )
    total_properties = prop_count_res.scalar() or 0

    val_count_res = await session.execute(
        select(func.count()).select_from(ValuationPrediction)
    )
    total_valuations = val_count_res.scalar() or 0

    loc_count_res = await session.execute(
        select(func.count()).select_from(Locality)
    )
    total_localities = loc_count_res.scalar() or 0

    user_count_res = await session.execute(
        select(func.count()).select_from(User)
    )
    total_users = user_count_res.scalar() or 0

    return {
        "total_properties": total_properties,
        "total_valuations": total_valuations,
        "total_localities": total_localities,
        "total_users": total_users,
        "active_users": total_users,
        "model_version": "heuristic-v1",
        "health_status": "healthy",
        "system_status": "healthy",
    }


@router.post("/trigger-valuations")
async def trigger_bulk_valuations(
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Trigger bulk valuation for unpredicted properties."""
    service = ValuationService(session)
    preds = await service.bulk_predict(limit=limit)
    return {
        "status": "success",
        "valuations_created": len(preds),
        "valuations_generated": len(preds),
    }
