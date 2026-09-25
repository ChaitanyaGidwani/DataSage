"""Unit tests for InvestmentService and ROI projection logic."""

from typing import Any
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from datasage.core.exceptions import NotFoundError
from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.services.investment_service import InvestmentService


@pytest.mark.asyncio
async def test_investment_analysis_success(mock_property: Property, mock_locality: Locality) -> None:
    """Test investment analysis calculations and 5-year projections."""
    session = AsyncMock()

    async def mock_execute(query: Any, *args: Any, **kwargs: Any) -> Any:
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
    service = InvestmentService(session)

    analysis = await service.analyze_property(str(mock_property.id))

    assert analysis.property_id == mock_property.id
    assert 30 <= analysis.investment_score <= 96
    assert analysis.investment_grade in [
        "High Growth Potential",
        "Strong Fundamentals",
        "Moderate Yield",
        "Conservative / End-User Focused",
    ]
    assert analysis.gross_rental_yield_pct > 0
    assert analysis.estimated_annual_rent > analysis.estimated_monthly_rent
    assert analysis.estimated_monthly_rent == int(analysis.estimated_annual_rent / 12)
    assert len(analysis.projections) == 5

    # Check compounding growth across years
    for i in range(1, len(analysis.projections)):
        assert analysis.projections[i].projected_value > analysis.projections[i - 1].projected_value
        assert analysis.projections[i].cumulative_gain_pct > analysis.projections[i - 1].cumulative_gain_pct

    assert analysis.projected_5yr_value == analysis.projections[-1].projected_value
    assert len(analysis.growth_catalysts) >= 1
    assert len(analysis.investment_risks) >= 1
    assert "cagr" in analysis.summary_verdict.lower()


@pytest.mark.asyncio
async def test_investment_analysis_not_found() -> None:
    """Test investment analysis raises NotFoundError when property missing."""
    session = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    session.execute.return_value = res

    service = InvestmentService(session)
    with pytest.raises(NotFoundError):
        await service.analyze_property(str(uuid.uuid4()))
