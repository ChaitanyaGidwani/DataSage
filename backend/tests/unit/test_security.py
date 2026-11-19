"""Unit tests for security, password hashing, and JWT tokens."""

from datetime import timedelta

from datasage.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)


def test_password_hashing() -> None:
    """Test that bcrypt hashes password and verifies correctly."""
    plain = "MySecretPassword123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_access_token_creation_and_verification() -> None:
    """Test creating and verifying an access token."""
    token = create_access_token(
        user_id="user-1234",
        email="test@datasage.ai",
        role="buyer",
    )
    assert isinstance(token, str)

    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "user-1234"
    assert payload["email"] == "test@datasage.ai"
    assert payload["role"] == "buyer"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_refresh_token_creation_and_verification() -> None:
    """Test creating and verifying a refresh token."""
    token = create_refresh_token(user_id="user-1234")
    assert isinstance(token, str)

    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "user-1234"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_expired_token_returns_none() -> None:
    """Test that expired tokens return None when verified."""
    expired_token = create_access_token(
        user_id="user-expired",
        email="expired@example.com",
        role="buyer",
        expires_delta=timedelta(seconds=-10),  # expired 10 seconds ago
    )
    payload = verify_token(expired_token)
    assert payload is None


def test_invalid_token_returns_none() -> None:
    """Test that tampered/garbage tokens return None."""
    assert verify_token("invalid.jwt.token") is None
    assert verify_token("") is None
