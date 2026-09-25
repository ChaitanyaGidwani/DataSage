"""Property search and detail endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.api.deps import get_current_user_optional
from datasage.core.database import get_session
from datasage.models.user import User
from datasage.schemas import CursorPagination, PaginatedResponse
from datasage.schemas.investment import InvestmentAnalysisResponse
from datasage.schemas.location import LocationScoreResponse
from datasage.schemas.property import (
    PropertyDetailResponse,
    PropertySummaryResponse,
    PropertyType,
    SortField,
    SortOrder,
)
from datasage.services.property_service import PropertyService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[PropertySummaryResponse])
async def search_properties(
    locality_id: int | None = None,
    city_id: int | None = None,
    bhk: int | None = Query(None, ge=1, le=10),
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
    property_type: PropertyType | None = None,
    min_area: float | None = Query(None, ge=0),
    max_area: float | None = None,
    furnishing: str | None = None,
    sort: SortField = SortField.RELEVANCE,
    order: SortOrder = SortOrder.DESC,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
) -> PaginatedResponse[PropertySummaryResponse]:
    """Search properties with filters, sorting, and pagination."""
    service = PropertyService(session)

    # Map sort field to model attribute
    sort_map = {
        SortField.LISTING_PRICE: "listing_price",
        SortField.AREA_SQFT: "area_sqft",
        SortField.LISTED_AT: "listed_at",
        SortField.LOCATION_SCORE: "cached_location_score",
        SortField.RELEVANCE: "listed_at",  # Default sort
    }

    summaries, next_cursor, total = await service.search(
        city_id=city_id,
        locality_id=locality_id,
        bhk=bhk,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type.value if property_type else None,
        min_area=min_area,
        max_area=max_area,
        furnishing=furnishing,
        sort=sort_map.get(sort, "listed_at"),
        order=order.value,
        limit=limit,
        cursor=cursor,
    )

    return PaginatedResponse(
        data=summaries,
        pagination=CursorPagination(
            next_cursor=next_cursor,
            has_more=next_cursor is not None,
            total_count=total,
        ),
    )


@router.get("/{property_id}", response_model=PropertyDetailResponse)
async def get_property_detail(
    property_id: str,
    session: AsyncSession = Depends(get_session),
) -> PropertyDetailResponse:
    """Get full property detail by ID."""
    service = PropertyService(session)
    return await service.get_detail(property_id)


@router.get("/{property_id}/valuation")
async def get_property_valuation_subroute(
    property_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Get AI valuation for a specific property (nested endpoint)."""
    from datasage.services.valuation_service import ValuationService

    service = ValuationService(session)
    return await service.predict_value(property_id)


@router.get("/{property_id}/location")
async def get_property_location_subroute(
    property_id: str,
    session: AsyncSession = Depends(get_session),
) -> LocationScoreResponse:
    """Get location intelligence for a specific property (nested endpoint)."""
    from datasage.services.location_service import LocationService

    service = LocationService(session)
    return await service.get_property_location_score(property_id)


@router.get("/{property_id}/investment")
async def get_property_investment_subroute(
    property_id: str,
    session: AsyncSession = Depends(get_session),
) -> InvestmentAnalysisResponse:
    """Get investment potential analysis for a specific property (nested endpoint)."""
    from datasage.services.investment_service import InvestmentService

    service = InvestmentService(session)
    return await service.analyze_property(property_id)


@router.get("/{property_id}/similar", response_model=list[PropertySummaryResponse])
async def get_similar_properties(
    property_id: str,
    limit: int = Query(4, ge=1, le=10),
    session: AsyncSession = Depends(get_session),
) -> list[PropertySummaryResponse]:
    """Get 3-5 similar properties based on locality, BHK, and price range."""
    service = PropertyService(session)
    return await service.get_similar(property_id, limit=limit)
