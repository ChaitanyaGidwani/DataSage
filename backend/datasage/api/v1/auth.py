"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.api.deps import get_current_user
from datasage.core.database import get_session
from datasage.models.user import User
from datasage.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from datasage.schemas.user import UserResponse, UserUpdateRequest
from datasage.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Register a new user account."""
    service = AuthService(session)
    return await service.register(body)


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Authenticate and receive JWT tokens."""
    service = AuthService(session)
    return await service.login(body.email, body.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Refresh an expired access token using a valid refresh token."""
    service = AuthService(session)
    result = await service.refresh_token(body.refresh_token)
    return TokenResponse(**result)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    """Get current user profile."""
    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        email_verified=user.email_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdateRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Update current user profile."""
    from datasage.repositories.user_repo import UserRepository

    repo = UserRepository(session)
    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        updated = await repo.update_profile(user.id, **update_data)
        user = updated or user

    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        email_verified=user.email_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )
