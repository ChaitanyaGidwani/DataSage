"""Property and PropertyImage models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datasage.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Property(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Core property listing entity."""

    __tablename__ = "property"

    city_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("city.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    locality_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locality.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    property_type: Mapped[str] = mapped_column(String(20), nullable=False)
    bhk: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    area_sqft: Mapped[float] = mapped_column(Float, nullable=False)
    listing_price: Mapped[int] = mapped_column(Integer, nullable=False)
    floor_number: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    total_floors: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    facing: Mapped[str | None] = mapped_column(String(20), nullable=True)
    construction_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    furnishing: Mapped[str | None] = mapped_column(String(20), nullable=True)
    parking_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    balcony_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    bathroom_count: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_source: Mapped[str] = mapped_column(String(30), nullable=False, default="seed")
    dataset_import_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Geolocation — populated from locality centroid or exact pin
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Denormalized cached scores (updated by scoring services)
    cached_location_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cached_investment_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    listed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    city = relationship("City", back_populates="properties", lazy="joined")
    locality = relationship("Locality", back_populates="properties", lazy="joined")
    images = relationship("PropertyImage", back_populates="property", lazy="selectin")
    location = relationship(
        "PropertyLocation", back_populates="property", uselist=False, lazy="selectin"
    )
    valuations = relationship("ValuationPrediction", back_populates="property", lazy="select")

    __table_args__ = (
        Index(
            "idx_property_search",
            "city_id",
            "locality_id",
            "bhk",
            "property_type",
            "listing_price",
        ),
        Index("idx_property_active", "is_active", "deleted_at"),
        Index("idx_property_geo", "latitude", "longitude"),
    )


class PropertyImage(UUIDMixin, Base):
    """Property image with ordering."""

    __tablename__ = "property_image"

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    display_order: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    property = relationship("Property", back_populates="images")
