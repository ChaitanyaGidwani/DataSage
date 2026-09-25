"""Pydantic schemas for geospatial and location intelligence."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class POIItem(BaseModel):
    """A point of interest near a property."""
    name: str
    category: str
    distance_meters: int
    distance_km: float
    travel_time_minutes_walk: int
    travel_time_minutes_drive: int


class LocationSubScores(BaseModel):
    """Granular subscores across categories (each 0 to 100)."""
    transit: int = Field(..., ge=0, le=100, description="Metro, bus, connectivity score")
    schools: int = Field(..., ge=0, le=100, description="Quality and proximity to schools")
    healthcare: int = Field(..., ge=0, le=100, description="Hospitals and clinics accessibility")
    shopping: int = Field(..., ge=0, le=100, description="Markets, supermarkets, malls")
    parks: int = Field(..., ge=0, le=100, description="Parks, gardens, and green spaces")
    dining: int = Field(..., ge=0, le=100, description="Restaurants, cafes, food hubs")


class LocationScoreResponse(BaseModel):
    """Complete location intelligence response for a property."""
    property_id: uuid.UUID
    composite_score: int = Field(..., ge=0, le=100, description="Overall weighted location score")
    rating_label: str = Field(..., description="e.g. Excellent, Very Good, Good, Fair, Needs Improvement")
    sub_scores: LocationSubScores
    nearest_metro: POIItem | None = None
    nearest_hospital: POIItem | None = None
    nearest_school: POIItem | None = None
    nearby_pois: list[POIItem] = []
    location_summary: str
