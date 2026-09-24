"""Property service — search, detail, and listing management."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.exceptions import NotFoundError
from datasage.repositories.property_repo import PropertyRepository
from datasage.repositories.locality_repo import LocalityRepository
from datasage.schemas.property import (
    LocalitySummary,
    PropertyDetailResponse,
    PropertyLocationResponse,
    PropertySummaryResponse,
)

logger = logging.getLogger(__name__)


class PropertyService:
    """Business logic for property search and details."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.property_repo = PropertyRepository(session)
        self.locality_repo = LocalityRepository(session)

    async def search(self, **params: Any) -> tuple[list[PropertySummaryResponse], str | None, int]:
        """Search properties with filters and pagination."""
        properties, next_cursor, total = await self.property_repo.search(**params)

        # Build summary responses
        summaries = []
        for prop in properties:
            # Get locality info
            locality = await self.locality_repo.get_by_id(prop.locality_id)
            locality_summary = LocalitySummary(
                id=prop.locality_id,
                name=locality.name if locality else "Unknown",
                city=locality.city.name if locality and locality.city else "",
            )

            # Primary image
            primary_image = next(
                (img.url for img in (prop.images or []) if img.is_primary),
                (prop.images[0].url if prop.images else None),
            )

            summaries.append(
                PropertySummaryResponse(
                    id=str(prop.id),
                    title=prop.title,
                    property_type=prop.property_type,
                    bhk=prop.bhk,
                    area_sqft=prop.area_sqft,
                    listing_price=prop.listing_price,
                    locality=locality_summary,
                    primary_image_url=primary_image,
                    location_score=prop.cached_location_score,
                    listed_at=prop.listed_at,
                )
            )

        return summaries, next_cursor, total

    async def get_detail(self, property_id: str) -> PropertyDetailResponse:
        """Get full property detail by ID."""
        prop = await self.property_repo.get_by_id(uuid.UUID(property_id))
        if not prop:
            raise NotFoundError("Property", property_id)

        # Locality
        locality = await self.locality_repo.get_by_id(prop.locality_id)
        locality_summary = LocalitySummary(
            id=prop.locality_id,
            name=locality.name if locality else "Unknown",
            city=locality.city.name if locality and locality.city else "",
        )

        # Location
        location = None
        if prop.location:
            location = PropertyLocationResponse(
                latitude=prop.latitude,
                longitude=prop.longitude,
                full_address=prop.location.full_address,
                pin_code=prop.location.pin_code,
            )
        elif prop.latitude is not None and prop.longitude is not None:
            location = PropertyLocationResponse(
                latitude=prop.latitude,
                longitude=prop.longitude,
            )

        # Images
        images = [
            {"url": img.url, "is_primary": img.is_primary, "display_order": img.display_order}
            for img in sorted(prop.images or [], key=lambda x: x.display_order)
        ]

        return PropertyDetailResponse(
            id=str(prop.id),
            title=prop.title,
            property_type=prop.property_type,
            bhk=prop.bhk,
            area_sqft=prop.area_sqft,
            listing_price=prop.listing_price,
            floor_number=prop.floor_number,
            total_floors=prop.total_floors,
            facing=prop.facing,
            construction_year=prop.construction_year,
            furnishing=prop.furnishing,
            parking_count=prop.parking_count,
            balcony_count=prop.balcony_count,
            bathroom_count=prop.bathroom_count,
            description=prop.description,
            data_source=prop.data_source,
            locality=locality_summary,
            location=location,
            images=images,
            listed_at=prop.listed_at,
            created_at=prop.created_at,
        )
