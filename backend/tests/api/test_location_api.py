"""API integration tests for location & geospatial intelligence endpoints."""

from fastapi.testclient import TestClient
from datasage.models.property import Property


def test_get_location_intelligence(client: TestClient, mock_property: Property):
    """Test GET /api/v1/location/{property_id} returns composite and sub-scores."""
    response = client.get(f"/api/v1/location/{mock_property.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["property_id"] == str(mock_property.id)
    assert "composite_score" in data
    assert "rating_label" in data
    assert "sub_scores" in data
    assert "transit" in data["sub_scores"]
    assert "schools" in data["sub_scores"]
    assert "healthcare" in data["sub_scores"]
    assert "shopping" in data["sub_scores"]
    assert "parks" in data["sub_scores"]
    assert "dining" in data["sub_scores"]
    assert "location_summary" in data
