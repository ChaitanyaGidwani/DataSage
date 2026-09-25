"""Unit tests for ComparisonService and property comparison matrix."""

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from datasage.core.exceptions import ValidationError
from datasage.models.property import Property
from datasage.models.reference import City, Locality
from datasage.services.comparison_service import ComparisonService


@pytest.mark.asyncio
async def test_compare_properties_requires_at_least_two():
    """Test validation error when comparing fewer than 2 properties."""
    session = AsyncMock()
    service = ComparisonService(session)

    with pytest.raises(ValidationError) as exc_info:
        await service.compare_properties([uuid.uuid4()])
    assert "at least 2" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_compare_properties_rejects_more_than_four():
    """Test validation error when comparing more than 4 properties."""
    session = AsyncMock()
    service = ComparisonService(session)

    five_ids = [uuid.uuid4() for _ in range(5)]
    with pytest.raises(ValidationError) as exc_info:
        await service.compare_properties(five_ids)
    assert "maximum of 4" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_compare_properties_success(mock_property: Property, mock_locality: Locality, mock_city: City):
    """Test side-by-side comparison of 2 properties."""
    # Create second property
    prop2_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
    prop2 = Property(
        id=prop2_id,
        city_id=1,
        locality_id=1,
        title="2 BHK Modern Flat in Sector 75, Noida",
        property_type="apartment",
        bhk=2,
        area_sqft=1100.0,
        listing_price=4800000,
        floor_number=3,
        total_floors=14,
        facing="north",
        construction_year=2022,
        furnishing="fully_furnished",
        parking_count=1,
        balcony_count=1,
        bathroom_count=2,
        description="Cozy 2 BHK in prime location.",
        data_source="seed",
        latitude=28.5710,
        longitude=77.3900,
        cached_location_score=80.0,
        is_active=True,
    )
    prop2.images = []

    session = AsyncMock()

    async def mock_execute(query, *args, **kwargs):
        res = MagicMock()
        q_str = str(query).lower()
        if "from property" in q_str:
            res.scalars.return_value.all.return_value = [mock_property, prop2]
        elif "from locality" in q_str:
            res.scalar_one_or_none.return_value = mock_locality
        elif "from city" in q_str:
            res.scalar_one_or_none.return_value = mock_city
        elif "from valuation_prediction" in q_str:
            res.scalar_one_or_none.return_value = None
        else:
            res.scalar_one_or_none.return_value = None
        return res

    session.execute.side_effect = mock_execute
    service = ComparisonService(session)

    # Mock valuation service predict_value
    service.valuation_service.predict_value = AsyncMock(return_value={
        "predicted_value": 5200000,
        "price_gap_pct": -5.0,
        "pricing_classification": "fair",
        "confidence_score": 0.85,
    })

    response = await service.compare_properties([mock_property.id, prop2.id])

    assert len(response.properties) == 2
    assert response.properties[0].id == mock_property.id
    assert response.properties[1].id == prop2.id
    assert response.summary.best_value_pick_id in [mock_property.id, prop2.id]
    assert response.summary.cheapest_per_sqft_id in [mock_property.id, prop2.id]
