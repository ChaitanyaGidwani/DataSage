"""Reference data models: City and Locality."""

from __future__ import annotations

from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datasage.models.base import Base


class City(Base):
    """City reference table — scopes all data for multi-city expansion."""

    __tablename__ = "city"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    bbox: Mapped[str | None] = mapped_column(Geography("POLYGON", srid=4326), nullable=True)
    scoring_weights: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    localities = relationship("Locality", back_populates="city", lazy="selectin")
    properties = relationship("Property", back_populates="city", lazy="select")


class Locality(Base):
    """Locality within a city — neighborhoods, sectors, colonies."""

    __tablename__ = "locality"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("city.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    centroid_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    centroid_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_price_per_sqft: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_trend_1y_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_trend_3y_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    city = relationship("City", back_populates="localities", lazy="joined")
    properties = relationship("Property", back_populates="locality", lazy="select")

    __table_args__ = (
        Index("idx_locality_city_name", "city_id", "name"),
    )
