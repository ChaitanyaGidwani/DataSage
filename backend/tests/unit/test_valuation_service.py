import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from datasage.core.exceptions import NotFoundError
from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.services.valuation_service import (
    ValuationService,
    _classify_pricing,
    _get_floor_tier,
)


def test_classify_pricing_logic() -> None:
    """Test price gap and classification logic."""
    # Underpriced (> 10% below predicted)
    classification, gap = _classify_pricing(listing_price=5000000, predicted=6000000)
    assert classification == "underpriced"
    assert round(gap, 2) == -16.67

    # Fair (within ±10%)
    classification, gap = _classify_pricing(listing_price=6200000, predicted=6000000)
    assert classification == "fair"
    assert round(gap, 2) == 3.33

    # Overpriced (> 10% above predicted)
    classification, gap = _classify_pricing(listing_price=7500000, predicted=6000000)
    assert classification == "overpriced"
    assert round(gap, 2) == 25.0

    # Zero predicted edge case
    classification, gap = _classify_pricing(listing_price=5000000, predicted=0)
    assert classification == "fair"
    assert gap == 0.0


def test_floor_tier_classification() -> None:
    """Test floor tier classification for various floor numbers."""
    assert _get_floor_tier(0, 10) == "ground"
    assert _get_floor_tier(2, 10) == "low"
    assert _get_floor_tier(6, 15) == "mid"
    assert _get_floor_tier(14, 20) == "high"
    assert _get_floor_tier(25, 30) == "penthouse"
    assert _get_floor_tier(None, 10) == "mid"


@pytest.mark.asyncio
async def test_predict_value_success(mock_property: Property, mock_locality: Locality) -> None:
    """Test successful valuation calculation with mock session."""
    session = AsyncMock()

    async def mock_execute(query: Any, *args: Any, **kwargs: Any) -> Any:
        res = MagicMock()
        q_str = str(query).lower()
        if "from property" in q_str:
            res.scalar_one_or_none.return_value = mock_property
        elif "from locality" in q_str:
            res.scalar_one_or_none.return_value = mock_locality
        elif "from model_version" in q_str:
            res.scalar_one_or_none.return_value = MagicMock()
        else:
            res.scalar_one_or_none.return_value = None
        return res

    session.execute.side_effect = mock_execute
    session.add = MagicMock()
    session.flush = AsyncMock()

    service = ValuationService(session)
    result = await service.predict_value(str(mock_property.id))

    assert result["property_id"] == str(mock_property.id)
    assert result["predicted_value"] > 0
    assert result["confidence_low"] < result["predicted_value"]
    assert result["confidence_high"] > result["predicted_value"]
    assert result["pricing_classification"] in ["underpriced", "fair", "overpriced"]
    assert "shap_values" in result
    assert "area_sqft" in result["shap_values"]
    assert "locality_avg_price" in result["shap_values"]


@pytest.mark.asyncio
async def test_predict_value_not_found() -> None:
    """Test valuation raises NotFoundError when property doesn't exist."""
    session = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    session.execute.return_value = res

    service = ValuationService(session)
    with pytest.raises(NotFoundError):
        await service.predict_value(str(uuid.uuid4()))
