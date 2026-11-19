"""PropertyLocation, POI, and NearbyPOI models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datasage.models.base import Base, UUIDMixin


class PropertyLocation(UUIDMixin, Base):
    """Property geolocation with computed location score."""

    __tablename__ = "property_location"

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    coordinates: Mapped[str] = mapped_column(
        Geography("POINT", srid=4326), nullable=False
    )
    full_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pin_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    location_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sub_scores: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    poi_last_refreshed: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    property = relationship("Property", back_populates="location")

    __table_args__ = (
        Index("idx_property_location_coords", "coordinates", postgresql_using="gist"),
    )


class POI(Base):
    """Points of Interest from OpenStreetMap."""

    __tablename__ = "poi"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("city.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    coordinates: Mapped[str] = mapped_column(
        Geography("POINT", srid=4326), nullable=False
    )
    osm_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    tags: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index("idx_poi_coords", "coordinates", postgresql_using="gist"),
        Index("idx_poi_city_category", "city_id", "category"),
    )


class NearbyPOI(Base):
    """Junction table linking PropertyLocation to nearby POIs with distance."""

    __tablename__ = "nearby_poi"

    property_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property_location.id", ondelete="CASCADE"), primary_key=True
    )
    poi_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("poi.id", ondelete="CASCADE"), primary_key=True
    )
    distance_meters: Mapped[float] = mapped_column(Float, nullable=False)
