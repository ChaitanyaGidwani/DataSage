"""User preferences endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.api.deps import get_current_user
from datasage.core.database import get_session
from datasage.models.user import User
from datasage.repositories.user_repo import PreferenceRepository
from datasage.schemas.user import UserPreferenceRequest, UserPreferenceResponse

router = APIRouter()


@router.get("", response_model=UserPreferenceResponse | None)
async def get_preferences(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserPreferenceResponse | None:
    """Get the current user's preferences."""
    repo = PreferenceRepository(session)
    pref = await repo.get_by_user(user.id)
    if not pref:
        return None

    commute = None
    if pref.commute_destination_lat and pref.commute_destination_lng:
        from datasage.schemas.user import CommuteDestination
        commute = CommuteDestination(
            latitude=pref.commute_destination_lat,
            longitude=pref.commute_destination_lng,
            label=pref.commute_destination_label or "",
        )

    return UserPreferenceResponse(
        id=str(pref.id),
        budget_min=pref.budget_min,
        budget_max=pref.budget_max,
        bhk_preferences=pref.bhk_preferences,
        preferred_locality_ids=pref.preferred_locality_ids,
        commute_destination=commute,
        lifestyle_priorities=pref.lifestyle_priorities,
        property_type_preferences=pref.property_type_preferences,
        updated_at=pref.updated_at,
    )


@router.put("", response_model=UserPreferenceResponse)
async def update_preferences(
    body: UserPreferenceRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserPreferenceResponse:
    """Create or update the current user's preferences."""
    repo = PreferenceRepository(session)

    data = body.model_dump(exclude_unset=True, exclude={"commute_destination"})
    if body.commute_destination:
        data["commute_destination_lat"] = body.commute_destination.latitude
        data["commute_destination_lng"] = body.commute_destination.longitude
        data["commute_destination_label"] = body.commute_destination.label

    pref = await repo.upsert(user.id, data)

    commute = None
    if pref.commute_destination_lat and pref.commute_destination_lng:
        from datasage.schemas.user import CommuteDestination
        commute = CommuteDestination(
            latitude=pref.commute_destination_lat,
            longitude=pref.commute_destination_lng,
            label=pref.commute_destination_label or "",
        )

    return UserPreferenceResponse(
        id=str(pref.id),
        budget_min=pref.budget_min,
        budget_max=pref.budget_max,
        bhk_preferences=pref.bhk_preferences,
        preferred_locality_ids=pref.preferred_locality_ids,
        commute_destination=commute,
        lifestyle_priorities=pref.lifestyle_priorities,
        property_type_preferences=pref.property_type_preferences,
        updated_at=pref.updated_at,
    )
