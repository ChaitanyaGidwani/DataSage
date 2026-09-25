"""API integration tests for localities endpoints."""

from fastapi.testclient import TestClient


def test_search_localities_success(client: TestClient) -> None:
    """Test searching localities by query string returns matches."""
    response = client.get("/api/v1/localities?q=Sector")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Sector 75"
    assert "avg_price_per_sqft" in data[0]


def test_get_locality_by_id_success(client: TestClient) -> None:
    """Test fetching single locality by ID."""
    response = client.get("/api/v1/localities/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Sector 75"


def test_get_locality_by_id_not_found(client: TestClient) -> None:
    """Test fetching non-existent locality returns 404."""
    response = client.get("/api/v1/localities/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
