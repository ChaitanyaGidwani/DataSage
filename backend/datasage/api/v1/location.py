"""Location & Geospatial intelligence API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import get_session
from datasage.schemas.location import LocationScoreResponse
from datasage.services.location_service import LocationService

router = APIRouter()


@router.get("/{property_id}", response_model=LocationScoreResponse)
async def get_property_location(
    property_id: str,
    session: AsyncSession = Depends(get_session),
) -> LocationScoreResponse:
    """Get composite location score, POI breakdown, and nearest transit/schools."""
    service = LocationService(session)
    return await service.get_property_location_score(property_id)
