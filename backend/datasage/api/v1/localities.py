"""Locality autocomplete endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import get_session
from datasage.repositories.locality_repo import LocalityRepository
from datasage.schemas.property import LocalityResponse

router = APIRouter()


@router.get("", response_model=list[LocalityResponse])
async def search_localities(
    q: str = Query("", min_length=1, description="Search query"),
    city_id: int | None = None,
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
) -> list[LocalityResponse]:
    """Search localities by name (autocomplete)."""
    repo = LocalityRepository(session)
    localities = await repo.search_by_name(q, city_id=city_id, limit=limit)
    return [
        LocalityResponse(
            id=loc.id,
            name=loc.name,
            city_id=loc.city_id,
            city_name=loc.city.name if loc.city else "",
            avg_price_per_sqft=loc.avg_price_per_sqft,
        )
        for loc in localities
    ]


@router.get("/{locality_id}", response_model=LocalityResponse)
async def get_locality(
    locality_id: int,
    session: AsyncSession = Depends(get_session),
) -> LocalityResponse:
    """Get a specific locality by ID."""
    repo = LocalityRepository(session)
    loc = await repo.get_by_id(locality_id)
    if not loc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Locality not found")
    return LocalityResponse(
        id=loc.id,
        name=loc.name,
        city_id=loc.city_id,
        city_name=loc.city.name if loc.city else "",
        avg_price_per_sqft=loc.avg_price_per_sqft,
    )
