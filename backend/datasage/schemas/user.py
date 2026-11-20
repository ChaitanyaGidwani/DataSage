"""User and preference schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Public user profile response."""

    id: str
    name: str
    email: str
    role: str
    email_verified: bool
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Profile update payload."""

    name: str | None = Field(None, min_length=1, max_length=100)


class CommuteDestination(BaseModel):
    """Commute destination with label."""

    latitude: float
    longitude: float
    label: str = ""


class UserPreferenceRequest(BaseModel):
    """Set/update user preferences for recommendations."""

    budget_min: int | None = Field(None, ge=0)
    budget_max: int | None = Field(None, ge=0)
    bhk_preferences: list[int] | None = None
    bhk_preference: list[int] | None = None
    preferred_locality_ids: list[int] | None = None
    preferred_localities: list[int] | None = None
    commute_destination: CommuteDestination | None = None
    lifestyle_priorities: list[str] | None = None
    property_type_preferences: list[str] | None = None
    property_types: list[str] | None = None


class UserPreferenceResponse(BaseModel):
    """Current user preferences."""

    id: str
    budget_min: int | None = None
    budget_max: int | None = None
    bhk_preferences: list[int] | None = None
    preferred_locality_ids: list[int] | None = None
    commute_destination: CommuteDestination | None = None
    lifestyle_priorities: list[str] | None = None
    property_type_preferences: list[str] | None = None
    updated_at: datetime

    model_config = {"from_attributes": True}
