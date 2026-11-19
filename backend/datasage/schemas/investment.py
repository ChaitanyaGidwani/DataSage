"""Pydantic schemas for investment analysis."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class YearlyProjection(BaseModel):
    year: int
    projected_value: int
    cumulative_gain_pct: float
    projected_rental_income: int


class InvestmentAnalysisResponse(BaseModel):
    """Investment analysis report for a residential property."""
    property_id: uuid.UUID
    investment_score: int = Field(..., ge=0, le=100, description="0-100 overall investment grade")
    investment_grade: str = Field(..., description="High Potential, Strong, Moderate, Speculative")

    # Rental metrics
    estimated_monthly_rent: int
    estimated_annual_rent: int
    gross_rental_yield_pct: float = Field(..., description="Annual rent / listing price * 100")
    delhi_ncr_average_yield_pct: float = 3.2

    # Capital appreciation
    locality_historical_cagr_pct: float = Field(..., description="3-year CAGR for this locality")
    projected_5yr_appreciation_pct: float
    projected_5yr_value: int

    # Infrastructure & Demand Drivers
    infrastructure_score: int = Field(..., ge=0, le=100)
    demand_supply_ratio: str = Field(..., description="High Demand, Balanced, High Supply")
    growth_catalysts: list[str] = []
    investment_risks: list[str] = []

    # 5-year forecast trajectory
    projections: list[YearlyProjection] = []
    summary_verdict: str
