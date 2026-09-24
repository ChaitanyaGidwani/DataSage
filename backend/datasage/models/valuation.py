"""ValuationPrediction and ModelVersion models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datasage.models.base import Base, UUIDMixin


class ModelVersion(UUIDMixin, Base):
    """Tracks trained ML model versions and their metrics."""

    __tablename__ = "model_version"

    version_label: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False, default="xgboost")
    hyperparameters: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    mape: Mapped[float | None] = mapped_column(Float, nullable=True)
    r_squared: Mapped[float | None] = mapped_column(Float, nullable=True)
    mae: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_sample_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ValuationPrediction(UUIDMixin, Base):
    """Stored valuation prediction for a property by a specific model version."""

    __tablename__ = "valuation_prediction"

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property.id", ondelete="CASCADE"), nullable=False
    )
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_version.id", ondelete="RESTRICT"), nullable=False
    )
    predicted_value: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_low: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_high: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    pricing_classification: Mapped[str] = mapped_column(String(20), nullable=False)
    price_gap_pct: Mapped[float] = mapped_column(Float, nullable=False)
    shap_values: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    feature_vector: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    property = relationship("Property", back_populates="valuations")
    model_version = relationship("ModelVersion")

    __table_args__ = (
        Index("idx_valuation_property", "property_id"),
        Index("idx_valuation_property_model", "property_id", "model_version_id", unique=True),
    )
