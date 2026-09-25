"""Property and locality schemas."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ── Enums ──────────────────────────────────────────────────────────────────

class PropertyType(StrEnum):
    APARTMENT = "apartment"
    BUILDER_FLOOR = "builder_floor"
    HOUSE = "house"
    PLOT = "plot"


class SortField(StrEnum):
    LISTING_PRICE = "listing_price"
    AREA_SQFT = "area_sqft"
    LISTED_AT = "listed_at"
    LOCATION_SCORE = "cached_location_score"
    RELEVANCE = "relevance"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


# ── Search params ──────────────────────────────────────────────────────────

class PropertySearchParams(BaseModel):
    """Query parameters for property search."""

    locality_id: int | None = None
    city_id: int | None = None
    bhk: int | None = Field(None, ge=1, le=10)
    min_price: int | None = Field(None, ge=0)
    max_price: int | None = Field(None, ge=0)
    property_type: PropertyType | None = None
    min_area: float | None = Field(None, ge=0)
    max_area: float | None = None
    furnishing: str | None = None
    sort: SortField = SortField.RELEVANCE
    order: SortOrder = SortOrder.DESC
    limit: int = Field(20, ge=1, le=100)
    cursor: str | None = None


# ── Locality ───────────────────────────────────────────────────────────────

class LocalityResponse(BaseModel):
    """Locality autocomplete result."""

    id: int
    name: str
    city_id: int
    city_name: str = ""
    avg_price_per_sqft: float | None = None

    model_config = {"from_attributes": True}


# ── Property responses ─────────────────────────────────────────────────────

class LocalitySummary(BaseModel):
    """Locality info embedded in property responses."""

    id: int
    name: str
    city: str = ""


class ValuationSummary(BaseModel):
    """Valuation summary embedded in property card."""

    predicted_value: int | None = None
    pricing_classification: str | None = None
    price_gap_pct: float | None = None


class PropertySummaryResponse(BaseModel):
    """Property card in search results."""

    id: str
    title: str
    property_type: str
    bhk: int
    area_sqft: float
    listing_price: int
    locality: LocalitySummary
    primary_image_url: str | None = None
    valuation_summary: ValuationSummary | None = None
    location_score: float | None = None
    listed_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyLocationResponse(BaseModel):
    """Property location detail."""

    latitude: float | None = None
    longitude: float | None = None
    full_address: str | None = None
    pin_code: str | None = None


class PropertyDetailResponse(BaseModel):
    """Full property detail page response."""

    id: str
    title: str
    property_type: str
    bhk: int
    area_sqft: float
    listing_price: int
    floor_number: int | None = None
    total_floors: int | None = None
    facing: str | None = None
    construction_year: int | None = None
    furnishing: str | None = None
    parking_count: int = 0
    balcony_count: int = 0
    bathroom_count: int | None = None
    description: str | None = None
    data_source: str
    locality: LocalitySummary
    location: PropertyLocationResponse | None = None
    images: list[dict[str, Any]] = []
    listed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
