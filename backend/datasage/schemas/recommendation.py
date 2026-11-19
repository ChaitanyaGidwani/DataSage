"""Pydantic schemas for personalized property recommendations."""

from __future__ import annotations

from pydantic import BaseModel, Field

from datasage.schemas.property import PropertySummaryResponse


class RecommendationItem(BaseModel):
    """A recommended property with suitability breakdown."""
    property: PropertySummaryResponse
    suitability_score: int = Field(..., ge=0, le=100, description="Overall match percentage")
    match_reasons: list[str] = Field(..., description="Key personalized reasons why this property was recommended")
    budget_fit: str = Field(..., description="Within budget, Below budget, Slightly above")
    location_match: str = Field(..., description="Preferred locality or high location score")


class RecommendationResponse(BaseModel):
    """List of tailored recommendations for the user."""
    items: list[RecommendationItem]
    total_matches: int
    user_preferences_applied: bool
    fallback_mode: bool = False
    message: str | None = None
