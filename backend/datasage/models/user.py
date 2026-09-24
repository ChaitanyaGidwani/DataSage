"""User and UserPreference models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datasage.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Platform user — supports buyer, investor, professional, admin roles."""

    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="buyer")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    preference = relationship("UserPreference", back_populates="user", uselist=False, lazy="selectin")
    saved_properties = relationship("SavedProperty", back_populates="user", lazy="select")
    search_history = relationship("SearchHistory", back_populates="user", lazy="select")


class UserPreference(UUIDMixin, TimestampMixin, Base):
    """User preferences for personalized recommendations."""

    __tablename__ = "user_preference"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bhk_preferences: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True)
    preferred_locality_ids: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True)
    commute_destination_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    commute_destination_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    commute_destination_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lifestyle_priorities: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    property_type_preferences: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="preference", lazy="joined")
