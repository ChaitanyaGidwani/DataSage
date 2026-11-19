"""Authentication service — registration, login, token management."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.config import settings
from datasage.core.exceptions import AuthenticationError, ConflictError
from datasage.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from datasage.repositories.user_repo import UserRepository
from datasage.schemas.auth import AuthResponse, RegisterRequest

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic for authentication and user management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, data: RegisterRequest) -> AuthResponse:
        """Register a new user account."""
        # Check for existing user
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictError(
                message="An account with this email already exists.",
                code="AUTH_EMAIL_EXISTS",
            )

        # Hash password in thread pool (CPU-bound bcrypt)
        password_hash = await asyncio.to_thread(hash_password, data.password)

        # Create user
        user = await self.user_repo.create(
            name=data.name,
            email=data.email,
            password_hash=password_hash,
        )

        # Generate tokens
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            role=user.role,
        )
        refresh_token = create_refresh_token(user_id=str(user.id))

        logger.info("User registered: %s", user.email)

        return AuthResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
            email_verified=user.email_verified,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError(
                message="Account has been deactivated",
                code="AUTH_ACCOUNT_INACTIVE",
            )

        # Verify password in thread pool (CPU-bound)
        is_valid = await asyncio.to_thread(verify_password, password, user.password_hash)
        if not is_valid:
            raise AuthenticationError("Invalid email or password")

        # Update last login
        await self.user_repo.update_last_login(user.id)

        # Generate tokens
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            role=user.role,
        )
        refresh_token = create_refresh_token(user_id=str(user.id))

        logger.info("User logged in: %s", user.email)

        return AuthResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
            email_verified=user.email_verified,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_token(self, refresh_token_str: str) -> dict[str, Any]:
        """Issue new access token from a valid refresh token."""
        payload = verify_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError(
                message="Invalid or expired refresh token",
                code="AUTH_INVALID_REFRESH",
            )

        user = await self.user_repo.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise AuthenticationError(
                message="User not found or inactive",
                code="AUTH_USER_INVALID",
            )

        # Rotate: issue new access + refresh token
        new_access = create_access_token(
            user_id=str(user.id),
            email=user.email,
            role=user.role,
        )
        new_refresh = create_refresh_token(user_id=str(user.id))

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
