"""API integration tests for authentication endpoints."""

import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from datasage.core.security import create_access_token, create_refresh_token, hash_password
from datasage.models.user import User


def test_auth_me_unauthorized(client: TestClient):
    """Test accessing /api/v1/auth/me without token returns 401/403."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code in [401, 403]


def test_auth_me_authorized(client: TestClient, user_access_token: str):
    """Test accessing /api/v1/auth/me with valid Bearer token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "priya@example.com"
    assert data["name"] == "Priya Sharma"
    assert data["role"] == "buyer"


def test_register_invalid_payload(client: TestClient):
    """Test registration endpoint rejects bad payload."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "invalid-email", "password": "123"},
    )
    assert response.status_code == 422


def test_login_invalid_credentials(client: TestClient):
    """Test login endpoint with non-existent email returns 401."""
    # When user is not found, AuthService raises AuthenticationError
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@datasage.ai", "password": "WrongPassword123"},
    )
    assert response.status_code == 401


def test_refresh_token_endpoint(client: TestClient, mock_user: User):
    """Test refreshing an access token with a valid refresh token."""
    refresh_tok = create_refresh_token(user_id=str(mock_user.id))
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_tok},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
