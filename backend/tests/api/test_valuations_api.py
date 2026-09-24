"""API integration tests for valuations endpoints."""

from fastapi.testclient import TestClient
from datasage.models.property import Property


def test_get_valuation(client: TestClient, mock_property: Property):
    """Test GET /api/v1/valuations/{property_id}."""
    response = client.get(f"/api/v1/valuations/{mock_property.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["property_id"] == str(mock_property.id)
    assert data["predicted_value"] > 0
    assert data["pricing_classification"] in ["underpriced", "fair", "overpriced"]


def test_bulk_valuations_requires_admin(client: TestClient, user_access_token: str):
    """Test bulk valuations endpoint rejects regular buyers with 403."""
    response = client.post(
        "/api/v1/valuations/bulk?limit=10",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 403


def test_bulk_valuations_admin_access(client: TestClient, admin_access_token: str):
    """Test bulk valuations endpoint accepts admin user."""
    response = client.post(
        "/api/v1/valuations/bulk?limit=5",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "generated" in data
    assert "predictions" in data
