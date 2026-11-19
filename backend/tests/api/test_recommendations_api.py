"""API integration tests for personalized recommendation endpoints."""

from fastapi.testclient import TestClient


def test_get_recommendations_unauthenticated(client: TestClient) -> None:
    """Test GET /api/v1/recommendations in unauthenticated fallback mode."""
    response = client.get("/api/v1/recommendations?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "user_preferences_applied" in data
    assert data["user_preferences_applied"] is False
    assert data["fallback_mode"] is True


def test_get_recommendations_authenticated(client: TestClient, user_access_token: str) -> None:
    """Test GET /api/v1/recommendations with authenticated user."""
    response = client.get(
        "/api/v1/recommendations?limit=5",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
