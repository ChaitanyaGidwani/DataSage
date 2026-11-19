"""User repository — data access layer for User and UserPreference."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.models.user import User, UserPreference


class UserRepository:
    """Data access for users."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(
                User.email == email.lower().strip(),
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str = "buyer",
    ) -> User:
        user = User(
            name=name,
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.now(UTC))
        )

    async def update_profile(self, user_id: uuid.UUID, **kwargs: Any) -> User | None:
        user = await self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.session.flush()
        return user


class PreferenceRepository:
    """Data access for user preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user(self, user_id: uuid.UUID) -> UserPreference | None:
        result = await self.session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: uuid.UUID, data: dict[str, Any]) -> UserPreference:
        pref = await self.get_by_user(user_id)
        if pref:
            for key, value in data.items():
                if hasattr(pref, key):
                    setattr(pref, key, value)
        else:
            pref = UserPreference(user_id=user_id, **data)
            self.session.add(pref)
        await self.session.flush()
        return pref
