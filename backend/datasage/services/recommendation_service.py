"""Personalized Recommendation Engine.

Implements content-based filtering with preference-weighted suitability scoring
as specified in docs/15-recommendation-engine.md.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from datasage.models.property import Property
from datasage.models.reference import City, Locality
from datasage.models.user import UserPreference
from datasage.models.valuation import ValuationPrediction
from datasage.schemas.property import LocalitySummary, PropertySummaryResponse, ValuationSummary
from datasage.schemas.recommendation import (
    RecommendationItem,
    RecommendationResponse,
)
from datasage.services.location_service import LocationService
from datasage.services.valuation_service import ValuationService

logger = logging.getLogger(__name__)


def _compute_budget_score(price: int, b_min: int | None, b_max: int | None) -> tuple[float, str]:
    """Score 0-1 on how well price fits the budget."""
    if b_min is None and b_max is None:
        return 0.85, "Within typical range"

    if b_min is None:
        assert b_max is not None
        min_val = int(b_max * 0.6)
        max_val = b_max
    elif b_max is None:
        min_val = b_min
        max_val = int(b_min * 1.5)
    else:
        min_val = b_min
        max_val = b_max

    if min_val <= price <= max_val:
        mid = (min_val + max_val) / 2
        half = (max_val - min_val) / 2 if max_val > min_val else 1.0
        dev = abs(price - mid) / half
        return max(0.7, 1.0 - (0.3 * dev)), "Perfect budget fit"
    elif price < min_val:
        gap = (min_val - price) / min_val
        return max(0.4, 1.0 - gap), "Below budget"
    else:
        gap = (price - max_val) / max_val
        return max(0.0, 0.5 - gap * 2), "Above budget"


class RecommendationService:
    """Generates personalized property recommendations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.location_service = LocationService(session)
        self.valuation_service = ValuationService(session)

    async def get_recommendations(
        self,
        user_id: uuid.UUID | None = None,
        limit: int = 10,
        city_id: int | None = None,
    ) -> RecommendationResponse:
        """Score candidate properties and return top matches."""
        # 1. Fetch user preference if user_id is provided
        pref: UserPreference | None = None
        if user_id:
            res = await self.session.execute(
                select(UserPreference).where(UserPreference.user_id == user_id)
            )
            pref = res.scalar_one_or_none()

        # 2. Fetch candidate active properties
        query = (
            select(Property)
            .options(selectinload(Property.images))
            .where(Property.is_active.is_(True), Property.deleted_at.is_(None))
        )
        if city_id:
            query = query.where(Property.city_id == city_id)
        query = query.limit(50)  # Evaluate top 50 candidates

        result = await self.session.execute(query)
        candidates = result.scalars().all()

        if not candidates:
            return RecommendationResponse(
                items=[],
                total_matches=0,
                user_preferences_applied=bool(pref),
                fallback_mode=True,
                message="No properties currently available for recommendation.",
            )

        scored_items: list[tuple[float, RecommendationItem]] = []

        pref_bhks: list[int] = pref.bhk_preferences if pref and pref.bhk_preferences else []
        pref_localities: list[int] = (
            pref.preferred_locality_ids if pref and pref.preferred_locality_ids else []
        )
        budget_min = pref.budget_min if pref else None
        budget_max = pref.budget_max if pref else None

        for prop in candidates:
            # Locality & City lookup
            loc_name = "Delhi-NCR"
            city_name = "Delhi-NCR"
            if prop.locality_id:
                l_res = await self.session.execute(
                    select(Locality).where(Locality.id == prop.locality_id)
                )
                loc = l_res.scalar_one_or_none()
                if loc:
                    loc_name = loc.name
            if prop.city_id:
                c_res = await self.session.execute(
                    select(City).where(City.id == prop.city_id)
                )
                c = c_res.scalar_one_or_none()
                if c:
                    city_name = c.name

            # Check valuation
            val_res = await self.session.execute(
                select(ValuationPrediction)
                .where(ValuationPrediction.property_id == prop.id)
                .order_by(ValuationPrediction.created_at.desc())
                .limit(1)
            )
            val = val_res.scalar_one_or_none()
            price_gap = val.price_gap_pct if val else 0.0

            # ── Component Scoring ──
            # 1. Budget match (weight 0.25)
            b_score, b_label = _compute_budget_score(prop.listing_price, budget_min, budget_max)

            # 2. BHK match (weight 0.15)
            bhk_score = 1.0 if not pref_bhks or prop.bhk in pref_bhks else 0.3

            # 3. Locality match (weight 0.15)
            loc_score = 1.0 if not pref_localities or prop.locality_id in pref_localities else 0.4

            # 4. Value score (weight 0.15)
            if val and val.pricing_classification == "underpriced":
                val_score = 1.0
            elif val and val.pricing_classification == "fair":
                val_score = 0.8
            else:
                val_score = 0.5

            # 5. Lifestyle & Location Score (weight 0.30)
            try:
                loc_intel = await self.location_service.get_property_location_score(str(prop.id))
                raw_loc_score = loc_intel.composite_score / 100.0
            except Exception:
                raw_loc_score = 0.72

            # Weighted composite suitability score (0 to 100)
            composite = (
                b_score * 0.25
                + bhk_score * 0.15
                + loc_score * 0.15
                + val_score * 0.15
                + raw_loc_score * 0.30
            ) * 100

            suitability = int(min(98, max(45, composite)))

            # Match reasons
            reasons = []
            if pref_bhks and prop.bhk in pref_bhks:
                reasons.append(f"Matches your {prop.bhk} BHK preference")
            if pref_localities and prop.locality_id in pref_localities:
                reasons.append(f"Located in your preferred area: {loc_name}")
            if val and val.pricing_classification == "underpriced":
                reasons.append(f"Attractive price: Underpriced by {abs(price_gap):.1f}% below fair market valuation")
            if raw_loc_score >= 0.80:
                reasons.append(f"Outstanding transit and infrastructure score ({int(raw_loc_score * 100)}/100)")
            if not reasons:
                reasons.append(f"Well-priced residential unit in thriving {loc_name}")

            summary_item = PropertySummaryResponse(
                id=str(prop.id),
                title=prop.title,
                property_type=prop.property_type,
                bhk=prop.bhk,
                area_sqft=prop.area_sqft,
                listing_price=prop.listing_price,
                locality=LocalitySummary(
                    id=prop.locality_id or 0,
                    name=loc_name,
                    city=city_name,
                ),
                primary_image_url=prop.images[0].url if prop.images else None,
                valuation_summary=ValuationSummary(
                    predicted_value=val.predicted_value,
                    pricing_classification=val.pricing_classification,
                    price_gap_pct=val.price_gap_pct,
                ) if val else None,
                location_score=round(raw_loc_score * 100.0, 1),
                listed_at=prop.listed_at,
            )

            rec_item = RecommendationItem(
                property=summary_item,
                suitability_score=suitability,
                match_reasons=reasons[:3],
                budget_fit=b_label,
                location_match=f"In {loc_name}",
            )

            scored_items.append((composite, rec_item))

        # Sort descending by suitability score
        scored_items.sort(key=lambda x: x[0], reverse=True)
        top_matches = [item for _, item in scored_items[:limit]]

        return RecommendationResponse(
            items=top_matches,
            total_matches=len(top_matches),
            user_preferences_applied=bool(pref),
            fallback_mode=not bool(pref),
            message=None if pref else "Displaying top regional market picks. Complete your profile preferences for tailored matching.",
        )
