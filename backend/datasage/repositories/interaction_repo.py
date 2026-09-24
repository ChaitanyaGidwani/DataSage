"""Interaction repositories: SavedProperty, SearchHistory."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from datasage.models.interaction import SavedProperty, SearchHistory
from datasage.models.property import Property


class SavedPropertyRepository:
    """Data access for saved/bookmarked properties."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[SavedProperty]:
        result = await self.session.execute(
            select(SavedProperty)
            .where(SavedProperty.user_id == user_id)
            .order_by(SavedProperty.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def save(self, user_id: uuid.UUID, property_id: uuid.UUID) -> SavedProperty:
        # Check if already saved
        existing = await self.session.execute(
            select(SavedProperty).where(
                SavedProperty.user_id == user_id,
                SavedProperty.property_id == property_id,
            )
        )
        existing_item = existing.scalar_one_or_none()
        if existing_item:
            return existing_item

        saved = SavedProperty(user_id=user_id, property_id=property_id)
        self.session.add(saved)
        await self.session.flush()
        return saved

    async def unsave(self, user_id: uuid.UUID, property_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            delete(SavedProperty).where(
                SavedProperty.user_id == user_id,
                SavedProperty.property_id == property_id,
            )
        )
        return result.rowcount > 0

    async def is_saved(self, user_id: uuid.UUID, property_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(func.count(SavedProperty.id)).where(
                SavedProperty.user_id == user_id,
                SavedProperty.property_id == property_id,
            )
        )
        return (result.scalar() or 0) > 0


class SearchHistoryRepository:
    """Data access for user search history."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user(
        self, user_id: uuid.UUID, limit: int = 20
    ) -> list[SearchHistory]:
        result = await self.session.execute(
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def record(
        self, user_id: uuid.UUID, query_params: dict, result_count: int
    ) -> SearchHistory:
        entry = SearchHistory(
            user_id=user_id,
            query_params=query_params,
            result_count=result_count,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def clear_for_user(self, user_id: uuid.UUID) -> int:
        result = await self.session.execute(
            delete(SearchHistory).where(SearchHistory.user_id == user_id)
        )
        return result.rowcount
