"""Personalized property recommendations API endpoints."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import get_session
from datasage.api.deps import get_current_user_optional
from datasage.models.user import User
from datasage.services.recommendation_service import RecommendationService
from datasage.schemas.recommendation import RecommendationResponse

router = APIRouter()


@router.get("", response_model=RecommendationResponse)
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    city_id: int | None = Query(None),
    current_user: User | None = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
) -> RecommendationResponse:
    """Get personalized recommendations based on user preference profile or top market picks."""
    user_id = current_user.id if current_user else None
    service = RecommendationService(session)
    return await service.get_recommendations(user_id=user_id, limit=limit, city_id=city_id)
