"""Recommendation and RecommendationReason models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datasage.models.base import Base, UUIDMixin


class Recommendation(UUIDMixin, Base):
    """A property recommended to a user with suitability scoring."""

    __tablename__ = "recommendation"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property.id", ondelete="CASCADE"), nullable=False
    )
    suitability_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    reasons = relationship("RecommendationReason", back_populates="recommendation", lazy="selectin")


class RecommendationReason(UUIDMixin, Base):
    """Natural-language explanation for why a property was recommended."""

    __tablename__ = "recommendation_reason"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recommendation.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason_text: Mapped[str] = mapped_column(String(500), nullable=False)
    contribution_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Relationships
    recommendation = relationship("Recommendation", back_populates="reasons")
