"""API integration tests for investment analysis endpoints."""

from fastapi.testclient import TestClient
from datasage.models.property import Property


def test_get_investment_analysis(client: TestClient, mock_property: Property) -> None:
    """Test GET /api/v1/investment/{property_id} returns ROI projections."""
    response = client.get(f"/api/v1/investment/{mock_property.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["property_id"] == str(mock_property.id)
    assert "investment_score" in data
    assert "investment_grade" in data
    assert "gross_rental_yield_pct" in data
    assert "projections" in data
    assert len(data["projections"]) == 5
    assert "summary_verdict" in data
