"""Locality repository — autocomplete search and lookup."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from datasage.models.reference import City, Locality


class LocalityRepository:
    """Data access for locality reference data."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search_by_name(
        self,
        query: str,
        city_id: int | None = None,
        limit: int = 10,
    ) -> list[Locality]:
        """Autocomplete search for locality names (case-insensitive prefix match)."""
        stmt = (
            select(Locality)
            .options(joinedload(Locality.city))
            .where(Locality.name.ilike(f"%{query}%"))
        )
        if city_id:
            stmt = stmt.where(Locality.city_id == city_id)
        stmt = stmt.order_by(Locality.name).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, locality_id: int) -> Locality | None:
        result = await self.session.execute(
            select(Locality)
            .options(joinedload(Locality.city))
            .where(Locality.id == locality_id)
        )
        return result.scalar_one_or_none()

    async def get_by_city(self, city_id: int) -> list[Locality]:
        result = await self.session.execute(
            select(Locality)
            .where(Locality.city_id == city_id)
            .order_by(Locality.name)
        )
        return list(result.scalars().all())

    async def get_all_cities(self) -> list[City]:
        result = await self.session.execute(
            select(City).where(City.is_active.is_(True)).order_by(City.name)
        )
        return list(result.scalars().all())
