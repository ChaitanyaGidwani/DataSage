from typing import Any
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from datasage.models.property import Property
from datasage.models.reference import City, Locality
from datasage.models.user import UserPreference
from datasage.services.recommendation_service import (
    RecommendationService,
    _compute_budget_score,
)


def test_compute_budget_score() -> None:
    """Test budget scoring curve."""
    # When no budget provided -> reasonable baseline
    score, label = _compute_budget_score(5000000, None, None)
    assert score == 0.85

    # Within budget range -> high score
    score, label = _compute_budget_score(6000000, 4000000, 8000000)
    assert 0.7 <= score <= 1.0
    assert "budget fit" in label.lower()

    # Below budget range
    score, label = _compute_budget_score(3000000, 4000000, 8000000)
    assert label == "Below budget"

    # Above budget range -> penalized
    score, label = _compute_budget_score(12000000, 4000000, 8000000)
    assert score < 0.5
    assert label == "Above budget"


@pytest.mark.asyncio
async def test_recommendations_fallback_mode_without_user(mock_property: Property, mock_locality: Locality, mock_city: City) -> None:
    """Test recommendation engine in fallback/popular mode without user_id."""
    session = AsyncMock()

    async def mock_execute(query: Any, *args: Any, **kwargs: Any) -> Any:
        res = MagicMock()
        q_str = str(query).lower()
        if "from property" in q_str:
            res.scalars.return_value.all.return_value = [mock_property]
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
    service = RecommendationService(session)

    response = await service.get_recommendations(user_id=None, limit=5)

    assert response.user_preferences_applied is False
    assert response.fallback_mode is True
    assert len(response.items) == 1
    assert response.items[0].suitability_score > 0
    assert len(response.items[0].match_reasons) > 0


@pytest.mark.asyncio
async def test_recommendations_with_user_preferences(mock_property: Property, mock_locality: Locality, mock_city: City) -> None:
    """Test recommendation engine tailoring scores to user preference."""
    pref = UserPreference(
        user_id=uuid.uuid4(),
        budget_min=5000000,
        budget_max=8000000,
        bhk_preferences=[3],
        preferred_locality_ids=[1],
        lifestyle_priorities=["metro", "schools"],
    )

    session = AsyncMock()

    async def mock_execute(query: Any, *args: Any, **kwargs: Any) -> Any:
        res = MagicMock()
        q_str = str(query).lower()
        if "from user_preference" in q_str:
            res.scalar_one_or_none.return_value = pref
        elif "from property" in q_str:
            res.scalars.return_value.all.return_value = [mock_property]
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
    service = RecommendationService(session)

    response = await service.get_recommendations(user_id=pref.user_id, limit=5)

    assert response.user_preferences_applied is True
    assert response.fallback_mode is False
    assert len(response.items) == 1
    assert response.items[0].suitability_score >= 70
    assert any("bhk" in r.lower() for r in response.items[0].match_reasons)
