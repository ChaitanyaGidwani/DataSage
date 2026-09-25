"""Pydantic schemas for property comparison."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ComparisonRequest(BaseModel):
    """Request payload for comparing multiple properties."""
    property_ids: list[uuid.UUID] = Field(
        ...,
        min_length=2,
        max_length=4,
        description="List of 2 to 4 property UUIDs to compare",
    )


class PropertyComparisonItem(BaseModel):
    """Normalized comparison metrics for a single property."""
    id: uuid.UUID
    title: str
    city: str
    locality: str
    property_type: str
    bhk: int
    area_sqft: float
    listing_price: int
    price_per_sqft: int
    floor_info: str
    furnishing: str | None
    facing: str | None
    parking_count: int
    construction_year: int | None
    images: list[str] = []

    # AI Valuation metrics
    predicted_value: int | None = None
    price_gap_pct: float | None = None
    pricing_classification: str | None = None
    valuation_confidence: float | None = None

    # Location & Investment
    location_score: int = 70
    investment_score: int = 65
    estimated_rental_yield_pct: float = 3.2

    # Comparative highlights
    key_advantages: list[str] = []
    key_tradeoffs: list[str] = []


class ComparisonSummary(BaseModel):
    """Overall comparative analysis summary across selected properties."""
    best_value_pick_id: uuid.UUID | None = None
    best_value_reason: str | None = None
    best_location_pick_id: uuid.UUID | None = None
    best_location_reason: str | None = None
    highest_investment_pick_id: uuid.UUID | None = None
    cheapest_per_sqft_id: uuid.UUID | None = None


class ComparisonResponse(BaseModel):
    """Full comparison response with items matrix and summary."""
    properties: list[PropertyComparisonItem]
    summary: ComparisonSummary
