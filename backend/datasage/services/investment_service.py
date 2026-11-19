"""Investment Analysis Service.

Computes investment scores, gross rental yields, locality appreciation CAGR,
and 5-year ROI forecasts for residential properties across Delhi-NCR.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.schemas.investment import (
    InvestmentAnalysisResponse,
    YearlyProjection,
)

logger = logging.getLogger(__name__)

# Historical 3-Year CAGR estimates and infra ratings for Delhi-NCR micromarkets
LOCALITY_INVESTMENT_DATA: dict[str, dict[str, Any]] = {
    # High Growth / Infrastructure corridors
    "Golf Course Extension": {"cagr": 11.2, "infra_score": 92, "rental_multiplier": 0.033, "catalysts": ["Dwarka Expressway completion", "Southern Peripheral Road cloverleaf", "Upcoming Cyber City 2"]},
    "Sector 150": {"cagr": 10.8, "infra_score": 90, "rental_multiplier": 0.034, "catalysts": ["Noida-Greater Noida Expressway connectivity", "Jewar International Airport corridor", "Sports City infrastructure"]},
    "Sector 82": {"cagr": 9.5, "infra_score": 86, "rental_multiplier": 0.036, "catalysts": ["Dwarka Expressway transit corridor", "Global City Gurgaon project", "Commercial sector expansion"]},
    "Sector 137": {"cagr": 8.6, "infra_score": 84, "rental_multiplier": 0.035, "catalysts": ["Noida Metro Aqua Line connectivity", "Advant Navis business park proximity", "FNG expressway corridor"]},
    "Sector 62": {"cagr": 7.4, "infra_score": 80, "rental_multiplier": 0.038, "catalysts": ["Established IT hub with continuous rental demand", "Blue Line Metro interchange", "Zero vacancy commercial offices"]},
    "Dwarka Sector 21": {"cagr": 8.1, "infra_score": 88, "rental_multiplier": 0.031, "catalysts": ["IICC Yashobhoomi Convention Centre", "Urban Extension Road II (UER-II)", "Airport Express link"]},
    "Golf Course Road": {"cagr": 8.9, "infra_score": 94, "rental_multiplier": 0.028, "catalysts": ["Ultra-luxury enclave with institutional landlords", "Rapid Metro connectivity", "Highest corporate tenant concentration"]},
    "DLF Phase 5": {"cagr": 8.4, "infra_score": 92, "rental_multiplier": 0.029, "catalysts": ["Horizon Center commercial nexus", "Prestigious residential demand", "Limited fresh inventory supply"]},
    "Indirapuram": {"cagr": 6.8, "infra_score": 75, "rental_multiplier": 0.037, "catalysts": ["Delhi-Meerut Expressway 14-lane signal-free drive", "Proposed Red Line Metro extension to Mohan Nagar"]},
    "Vasant Kunj": {"cagr": 6.5, "infra_score": 82, "rental_multiplier": 0.027, "catalysts": ["South Delhi institutional zone", "IGIA Terminal 3 adjacency", "Strict supply cap"]},
}

DEFAULT_INVESTMENT_DATA = {
    "cagr": 7.5,
    "infra_score": 75,
    "rental_multiplier": 0.032,
    "catalysts": ["Delhi-NCR regional transit expansion", "Ongoing urban infrastructure upgrades"],
}


class InvestmentService:
    """Service for analyzing property ROI, yields, and growth potential."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def analyze_property(self, property_id: str) -> InvestmentAnalysisResponse:
        """Generate comprehensive investment metrics for a property."""
        result = await self.session.execute(
            select(Property).where(Property.id == uuid.UUID(property_id))
        )
        prop = result.scalar_one_or_none()
        if not prop:
            from datasage.core.exceptions import NotFoundError
            raise NotFoundError("Property", property_id)

        # Get locality name
        locality_name = "Delhi-NCR"
        if prop.locality_id:
            loc_res = await self.session.execute(
                select(Locality).where(Locality.id == prop.locality_id)
            )
            loc = loc_res.scalar_one_or_none()
            if loc:
                locality_name = loc.name

        inv_data = LOCALITY_INVESTMENT_DATA.get(locality_name, DEFAULT_INVESTMENT_DATA)
        cagr = inv_data["cagr"]
        infra_score = inv_data["infra_score"]
        base_yield = inv_data["rental_multiplier"]

        # Adjust yield based on BHK: smaller units produce higher yields
        if prop.bhk == 1:
            yield_pct = (base_yield * 1.20) * 100
        elif prop.bhk == 2:
            yield_pct = (base_yield * 1.08) * 100
        elif prop.bhk == 3:
            yield_pct = base_yield * 100
        else:
            yield_pct = (base_yield * 0.90) * 100

        yield_pct = round(max(2.1, min(4.8, yield_pct)), 2)

        # Rental income calculations
        annual_rent = int(prop.listing_price * (yield_pct / 100.0))
        monthly_rent = int(annual_rent / 12)

        # 5-Year Capital Appreciation Projections (compounded with slight market moderation)
        projections: list[YearlyProjection] = []
        current_val = float(prop.listing_price)
        annual_rent_proj = annual_rent

        for yr in range(1, 6):
            # Compound appreciation with 5% annual rental growth
            current_val = current_val * (1.0 + (cagr / 100.0))
            cum_gain = ((current_val - prop.listing_price) / prop.listing_price) * 100
            annual_rent_proj = int(annual_rent_proj * 1.05)

            projections.append(
                YearlyProjection(
                    year=yr,
                    projected_value=int(current_val),
                    cumulative_gain_pct=round(cum_gain, 1),
                    projected_rental_income=annual_rent_proj,
                )
            )

        proj_5yr_val = projections[-1].projected_value
        proj_5yr_gain_pct = projections[-1].cumulative_gain_pct

        # Composite Investment Score (0 to 100)
        # Weights: 40% CAGR growth potential, 30% Infrastructure score, 30% Rental Yield
        cagr_normalized = min(100, int((cagr / 12.0) * 100))
        yield_normalized = min(100, int((yield_pct / 4.5) * 100))
        investment_score = int(
            cagr_normalized * 0.40
            + infra_score * 0.30
            + yield_normalized * 0.30
        )
        investment_score = max(30, min(96, investment_score))

        # Grade
        if investment_score >= 82:
            grade = "High Growth Potential"
        elif investment_score >= 70:
            grade = "Strong Fundamentals"
        elif investment_score >= 55:
            grade = "Moderate Yield"
        else:
            grade = "Conservative / End-User Focused"

        # Catalysts & Risks
        catalysts = inv_data.get("catalysts", ["Transit corridor upgrade"])
        risks = []
        if prop.construction_year and (2026 - prop.construction_year) > 15:
            risks.append("Aging property requires renovation / higher ongoing maintenance")
        if yield_pct < 2.5:
            risks.append("Lower gross rental yield typical of high-ticket luxury segments")
        if not risks:
            risks.append("Market liquidity subject to regional real-estate cycles")

        verdict = (
            f"Properties in {locality_name} benefit from a {cagr}% 3-year historical CAGR "
            f"and an infrastructure score of {infra_score}/100. With an estimated gross yield "
            f"of {yield_pct}%, this asset offers a projected 5-year capital appreciation of "
            f"~{proj_5yr_gain_pct}%."
        )

        return InvestmentAnalysisResponse(
            property_id=prop.id,
            investment_score=investment_score,
            investment_grade=grade,
            estimated_monthly_rent=monthly_rent,
            estimated_annual_rent=annual_rent,
            gross_rental_yield_pct=yield_pct,
            delhi_ncr_average_yield_pct=3.2,
            locality_historical_cagr_pct=cagr,
            projected_5yr_appreciation_pct=proj_5yr_gain_pct,
            projected_5yr_value=proj_5yr_val,
            infrastructure_score=infra_score,
            demand_supply_ratio="High Demand" if investment_score >= 75 else "Balanced",
            growth_catalysts=catalysts,
            investment_risks=risks,
            projections=projections,
            summary_verdict=verdict,
        )
