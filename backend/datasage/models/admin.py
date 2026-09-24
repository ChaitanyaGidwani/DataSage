"""Admin models: Dataset, DatasetImport, DataQualityReport."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datasage.models.base import Base, TimestampMixin, UUIDMixin


class Dataset(UUIDMixin, TimestampMixin, Base):
    """A named collection of property data uploaded by an admin."""

    __tablename__ = "dataset"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    property_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    imports = relationship("DatasetImport", back_populates="dataset", lazy="selectin")


class DatasetImport(UUIDMixin, Base):
    """An individual import operation within a dataset."""

    __tablename__ = "dataset_import"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quarantined_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="processing")
    error_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    imported_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="imports")
    quality_reports = relationship("DataQualityReport", back_populates="dataset_import", lazy="selectin")


class DataQualityReport(UUIDMixin, Base):
    """Data quality report generated after an import."""

    __tablename__ = "data_quality_report"

    dataset_import_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dataset_import.id", ondelete="CASCADE"), nullable=False, index=True
    )
    issues: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    total_issues: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    validity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    dataset_import = relationship("DatasetImport", back_populates="quality_reports")
