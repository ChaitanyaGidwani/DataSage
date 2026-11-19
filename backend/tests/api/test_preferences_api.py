"""API integration tests for user preferences endpoints."""

from fastapi.testclient import TestClient


def test_get_preferences_unauthorized(client: TestClient) -> None:
    """Test GET /api/v1/preferences requires auth."""
    response = client.get("/api/v1/preferences")
    assert response.status_code in [401, 403]


def test_get_preferences_authorized(client: TestClient, user_access_token: str) -> None:
    """Test GET /api/v1/preferences with valid token."""
    response = client.get(
        "/api/v1/preferences",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 200


def test_update_preferences(client: TestClient, user_access_token: str) -> None:
    """Test PUT /api/v1/preferences updating budget and lifestyle priorities."""
    payload = {
        "budget_min": 4500000,
        "budget_max": 8500000,
        "bhk_preferences": [2, 3],
        "lifestyle_priorities": ["metro", "schools", "parks"],
    }
    response = client.put(
        "/api/v1/preferences",
        json=payload,
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["budget_min"] == 4500000
    assert data["budget_max"] == 8500000
    assert data["bhk_preferences"] == [2, 3]
