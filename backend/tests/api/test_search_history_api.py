"""API integration tests for search history endpoints."""

from fastapi.testclient import TestClient


def test_list_search_history_unauthorized(client: TestClient) -> None:
    """Test GET /api/v1/search-history requires auth."""
    response = client.get("/api/v1/search-history")
    assert response.status_code in [401, 403]


def test_list_search_history_authorized(client: TestClient, user_access_token: str) -> None:
    """Test GET /api/v1/search-history returns history for user."""
    response = client.get(
        "/api/v1/search-history",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_clear_search_history_authorized(client: TestClient, user_access_token: str) -> None:
    """Test DELETE /api/v1/search-history clears history and returns 204."""
    response = client.delete(
        "/api/v1/search-history",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 204
