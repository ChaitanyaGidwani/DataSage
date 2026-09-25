"""API integration tests for saved properties endpoints."""

from fastapi.testclient import TestClient


def test_list_saved_unauthorized(client: TestClient) -> None:
    """Test GET /api/v1/saved-properties requires auth."""
    response = client.get("/api/v1/saved-properties")
    assert response.status_code in [401, 403]


def test_list_saved_authorized(client: TestClient, user_access_token: str) -> None:
    """Test GET /api/v1/saved-properties returns saved list for user."""
    response = client.get(
        "/api/v1/saved-properties",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_save_property_invalid_uuid(client: TestClient, user_access_token: str) -> None:
    """Test POST /api/v1/saved-properties rejects invalid property_id format with 422."""
    response = client.post(
        "/api/v1/saved-properties",
        json={"property_id": "not-a-valid-uuid"},
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 422
