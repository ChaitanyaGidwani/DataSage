"""Unit tests for LocationService and geospatial scoring logic."""

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from datasage.core.exceptions import NotFoundError
from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.services.location_service import (
    LocationService,
    _distance_to_subscore,
)


def test_distance_to_subscore():
    """Test mapping distances to 0-100 scores."""
    # Under walk distance -> 85-100
    score_walk = _distance_to_subscore(0.2, max_walk_km=0.8, max_good_km=2.5)
    assert 85 <= score_walk <= 100

    # Between walk and good distance -> 60-85
    score_mid = _distance_to_subscore(1.5, max_walk_km=0.8, max_good_km=2.5)
    assert 60 <= score_mid <= 85

    # Far distance -> decayed score
    score_far = _distance_to_subscore(5.0, max_walk_km=0.8, max_good_km=2.5)
    assert score_far < 60
    assert score_far >= 20  # minimum threshold


@pytest.mark.asyncio
async def test_get_property_location_score_success(mock_property: Property, mock_locality: Locality):
    """Test full location intelligence response generation."""
    session = AsyncMock()

    async def mock_execute(query, *args, **kwargs):
        res = MagicMock()
        q_str = str(query).lower()
        if "from property" in q_str:
            res.scalar_one_or_none.return_value = mock_property
        elif "from locality" in q_str:
            res.scalar_one_or_none.return_value = mock_locality
        else:
            res.scalar_one_or_none.return_value = None
        return res

    session.execute.side_effect = mock_execute
    service = LocationService(session)

    response = await service.get_property_location_score(str(mock_property.id))

    assert response.property_id == mock_property.id
    assert 1 <= response.composite_score <= 99
    assert response.rating_label in ["Excellent", "Very Good", "Good", "Moderate", "Developing Connectivity"]
    assert response.sub_scores.transit >= 0
    assert response.sub_scores.schools >= 0
    assert response.sub_scores.healthcare >= 0
    assert response.sub_scores.shopping >= 0
    assert response.sub_scores.parks >= 0
    assert response.sub_scores.dining >= 0
    assert response.nearest_metro is not None
    assert response.nearest_hospital is not None
    assert response.nearest_school is not None
    assert len(response.nearby_pois) >= 3
    assert "location intelligence" in response.location_summary.lower()


@pytest.mark.asyncio
async def test_location_score_property_not_found():
    """Test location service NotFoundError when property missing."""
    session = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    session.execute.return_value = res

    service = LocationService(session)
    with pytest.raises(NotFoundError):
        await service.get_property_location_score(str(uuid.uuid4()))
