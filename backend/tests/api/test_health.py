"""API integration tests for /health system status endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health endpoint returns status 200 and correct JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "env" in data
