"""Valuation service — ML-based property price prediction.

For MVP, uses a statistical heuristic model based on locality averages,
BHK multipliers, and property-feature adjustments. This produces realistic
valuations without requiring a trained XGBoost model file.

Phase 2 will swap this for a trained XGBoost model with SHAP explanations.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.models.valuation import ModelVersion, ValuationPrediction

logger = logging.getLogger(__name__)

# ── Feature weights for the heuristic model ────────────────────────────────

BHK_MULTIPLIERS = {1: 0.55, 2: 0.80, 3: 1.00, 4: 1.30, 5: 1.60}

FURNISHING_ADJUSTMENTS = {
    "fully_furnished": 1.08,
    "semi_furnished": 1.03,
    "unfurnished": 1.00,
    None: 1.00,
}

FLOOR_ADJUSTMENTS = {
    "ground": 0.95,   # Ground floor is less desirable
    "low": 0.98,      # 1-3
    "mid": 1.02,      # 4-10
    "high": 1.05,     # 11-20
    "penthouse": 1.10, # 20+
}

FACING_ADJUSTMENTS = {
    "east": 1.03,
    "north_east": 1.02,
    "north": 1.01,
    "south_east": 1.01,
    "west": 0.99,
    "south": 0.98,
    "south_west": 0.98,
    "north_west": 0.99,
    None: 1.00,
}


def _get_floor_tier(floor: int | None, total: int | None) -> str:
    if floor is None:
        return "mid"
    if floor == 0:
        return "ground"
    if floor <= 3:
        return "low"
    if floor <= 10:
        return "mid"
    if floor <= 20:
        return "high"
    return "penthouse"


def _classify_pricing(listing_price: int, predicted: int) -> tuple[str, float]:
    """Classify as underpriced/fair/overpriced with gap percentage."""
    if predicted == 0:
        return "fair", 0.0
    gap_pct = ((listing_price - predicted) / predicted) * 100
    if gap_pct < -10:
        return "underpriced", gap_pct
    elif gap_pct > 10:
        return "overpriced", gap_pct
    return "fair", gap_pct


class ValuationService:
    """Business logic for property valuation predictions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def predict_value(self, property_id: str) -> dict[str, Any]:
        """Generate a valuation prediction for a single property."""
        # Fetch property
        result = await self.session.execute(
            select(Property).where(Property.id == uuid.UUID(property_id))
        )
        prop = result.scalar_one_or_none()
        if not prop:
            from datasage.core.exceptions import NotFoundError
            raise NotFoundError("Property", property_id)

        # Check Redis cache for recent valuation prediction
        from datasage.core.config import settings
        from datasage.core.redis import cache_get_json, cache_set_json

        cache_key = f"valuation:{property_id}"
        cached = await cache_get_json(cache_key)
        if isinstance(cached, dict):
            return cached

        # Fetch locality for avg_price_per_sqft
        loc_result = await self.session.execute(
            select(Locality).where(Locality.id == prop.locality_id)
        )
        locality = loc_result.scalar_one_or_none()
        base_price_sqft = locality.avg_price_per_sqft if locality and locality.avg_price_per_sqft else 7000

        # ── Heuristic valuation model ──────────────────────────────────────
        bhk_mult = BHK_MULTIPLIERS.get(prop.bhk, 1.0)
        furnish_adj = FURNISHING_ADJUSTMENTS.get(prop.furnishing, 1.0)
        floor_tier = _get_floor_tier(prop.floor_number, prop.total_floors)
        floor_adj = FLOOR_ADJUSTMENTS.get(floor_tier, 1.0)
        facing_adj = FACING_ADJUSTMENTS.get(prop.facing, 1.0)

        # Age adjustment: newer properties command premium
        age_adj = 1.0
        if prop.construction_year:
            age = datetime.now().year - prop.construction_year
            if age <= 2:
                age_adj = 1.06
            elif age <= 5:
                age_adj = 1.03
            elif age <= 10:
                age_adj = 1.00
            elif age <= 20:
                age_adj = 0.95
            else:
                age_adj = 0.88

        # Parking premium
        parking_adj = 1.0 + (prop.parking_count * 0.015)

        # Compute predicted price
        adjusted_sqft = base_price_sqft * bhk_mult * furnish_adj * floor_adj * facing_adj * age_adj * parking_adj
        predicted_value = int(adjusted_sqft * prop.area_sqft)

        # Confidence band (±8-15% depending on data quality)
        confidence_pct = 0.10
        confidence_low = int(predicted_value * (1 - confidence_pct))
        confidence_high = int(predicted_value * (1 + confidence_pct))
        confidence_score = 0.78  # Heuristic model baseline confidence

        # Classify pricing
        classification, gap_pct = _classify_pricing(prop.listing_price, predicted_value)

        # Feature contributions (simulate SHAP-like explanations)
        shap_values = {
            "area_sqft": round(prop.area_sqft * base_price_sqft * 0.4, 0),
            "locality_avg_price": round(base_price_sqft, 0),
            "bhk": round((bhk_mult - 1.0) * predicted_value * 0.2, 0),
            "furnishing": round((furnish_adj - 1.0) * predicted_value, 0),
            "floor": round((floor_adj - 1.0) * predicted_value, 0),
            "facing": round((facing_adj - 1.0) * predicted_value, 0),
            "age": round((age_adj - 1.0) * predicted_value, 0),
            "parking": round((parking_adj - 1.0) * predicted_value, 0),
        }

        # Ensure baseline heuristic model version exists in DB
        heuristic_model_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        mv_res = await self.session.execute(
            select(ModelVersion).where(ModelVersion.id == heuristic_model_id)
        )
        if not mv_res.scalar_one_or_none():
            mv = ModelVersion(
                id=heuristic_model_id,
                version_label="v0.1-heuristic",
                algorithm="heuristic",
                is_active=True,
            )
            self.session.add(mv)
            await self.session.flush()

        # Store prediction
        prediction = ValuationPrediction(
            property_id=prop.id,
            model_version_id=heuristic_model_id,
            predicted_value=predicted_value,
            confidence_low=confidence_low,
            confidence_high=confidence_high,
            confidence_score=confidence_score,
            pricing_classification=classification,
            price_gap_pct=round(gap_pct, 2),
            shap_values=shap_values,
        )
        self.session.add(prediction)
        await self.session.flush()

        response_data = {
            "property_id": str(prop.id),
            "listing_price": prop.listing_price,
            "predicted_value": predicted_value,
            "confidence_low": confidence_low,
            "confidence_high": confidence_high,
            "confidence_score": confidence_score,
            "pricing_classification": classification,
            "price_gap_pct": round(gap_pct, 2),
            "shap_values": shap_values,
        }
        await cache_set_json(cache_key, response_data, ttl=settings.ML_PREDICTION_CACHE_TTL)
        return response_data

    async def bulk_predict(self, limit: int = 100) -> list[dict[str, Any]]:
        """Generate valuations for all properties that don't have one yet."""
        # Find properties without predictions
        subq = select(ValuationPrediction.property_id)
        result = await self.session.execute(
            select(Property.id)
            .where(Property.is_active.is_(True), Property.deleted_at.is_(None))
            .where(Property.id.notin_(subq))
            .limit(limit)
        )
        property_ids = [str(row[0]) for row in result.all()]

        predictions = []
        for pid in property_ids:
            try:
                pred = await self.predict_value(pid)
                predictions.append(pred)
            except Exception as e:
                logger.warning("Failed to predict for %s: %s", pid, e)
                continue

        logger.info("Generated %d valuations in bulk", len(predictions))
        return predictions
