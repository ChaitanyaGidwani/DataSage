"""API integration tests for admin endpoints."""

from fastapi.testclient import TestClient


def test_admin_stats_endpoint(client: TestClient):
    """Test GET /api/v1/admin/stats returns aggregate platform statistics."""
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_properties" in data
    assert "total_valuations" in data
    assert "total_localities" in data
    assert "total_users" in data
    assert "system_status" in data


def test_trigger_bulk_valuations_endpoint(client: TestClient):
    """Test POST /api/v1/admin/trigger-valuations runs bulk generation."""
    response = client.post("/api/v1/admin/trigger-valuations?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "valuations_generated" in data
