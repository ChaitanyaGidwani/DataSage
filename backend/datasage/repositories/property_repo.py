"""Property repository — search, filter, paginate."""

from __future__ import annotations

import base64
import json
import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from datasage.models.property import Property


class PropertyRepository:
    """Data access for properties with search, filtering, and cursor pagination."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, property_id: uuid.UUID) -> Property | None:
        result = await self.session.execute(
            select(Property)
            .options(selectinload(Property.images), selectinload(Property.location))
            .where(Property.id == property_id, Property.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Property]:
        result = await self.session.execute(
            select(Property)
            .options(selectinload(Property.images))
            .where(Property.id.in_(ids), Property.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def search(
        self,
        *,
        city_id: int | None = None,
        locality_id: int | None = None,
        bhk: int | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        property_type: str | None = None,
        min_area: float | None = None,
        max_area: float | None = None,
        furnishing: str | None = None,
        sort: str = "listed_at",
        order: str = "desc",
        limit: int = 20,
        cursor: str | None = None,
    ) -> tuple[list[Property], str | None, int]:
        """Search properties with filters, sorting, and cursor pagination.

        Returns: (properties, next_cursor, total_count)
        """
        # Base query
        query = (
            select(Property)
            .options(selectinload(Property.images))
            .where(Property.is_active.is_(True), Property.deleted_at.is_(None))
        )
        count_query = select(func.count(Property.id)).where(
            Property.is_active.is_(True), Property.deleted_at.is_(None)
        )

        # Apply filters
        filters = []
        if city_id:
            filters.append(Property.city_id == city_id)
        if locality_id:
            filters.append(Property.locality_id == locality_id)
        if bhk:
            filters.append(Property.bhk == bhk)
        if min_price is not None:
            filters.append(Property.listing_price >= min_price)
        if max_price is not None:
            filters.append(Property.listing_price <= max_price)
        if property_type:
            filters.append(Property.property_type == property_type)
        if min_area is not None:
            filters.append(Property.area_sqft >= min_area)
        if max_area is not None:
            filters.append(Property.area_sqft <= max_area)
        if furnishing:
            filters.append(Property.furnishing == furnishing)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Total count
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar() or 0

        # Sorting
        sort_column = getattr(Property, sort, Property.listed_at) or Property.created_at
        if order == "asc":
            query = query.order_by(sort_column.asc(), Property.id.asc())
        else:
            query = query.order_by(sort_column.desc(), Property.id.desc())

        # Cursor pagination
        if cursor:
            try:
                cursor_data = json.loads(base64.b64decode(cursor).decode())
                cursor_id = uuid.UUID(cursor_data["id"])
                # Simple approach: filter by id for cursor
                if order == "desc":
                    query = query.where(Property.id < cursor_id)
                else:
                    query = query.where(Property.id > cursor_id)
            except (ValueError, KeyError):
                pass  # Invalid cursor — ignore, return from beginning

        # Fetch limit + 1 to determine has_more
        query = query.limit(limit + 1)
        result = await self.session.execute(query)
        properties = list(result.scalars().all())

        # Build next cursor
        next_cursor = None
        if len(properties) > limit:
            properties = properties[:limit]
            last = properties[-1]
            cursor_payload = json.dumps({"id": str(last.id)})
            next_cursor = base64.b64encode(cursor_payload.encode()).decode()

        return properties, next_cursor, total_count

    async def create_bulk(self, properties: list[Property]) -> list[Property]:
        """Bulk insert properties."""
        self.session.add_all(properties)
        await self.session.flush()
        return properties
