"""Unit tests for Pydantic request and response schemas."""

import uuid

import pytest
from pydantic import ValidationError

from datasage.schemas.auth import RegisterRequest
from datasage.schemas.comparison import ComparisonRequest
from datasage.schemas.user import UserPreferenceRequest


def test_register_request_valid() -> None:
    """Test valid registration payload."""
    req = RegisterRequest(
        name="Rahul Verma",
        email="rahul@example.com",
        password="ValidPassword123",
    )
    assert req.name == "Rahul Verma"
    assert req.email == "rahul@example.com"


def test_register_request_invalid_email() -> None:
    """Test invalid email raises ValidationError."""
    with pytest.raises(ValidationError):
        RegisterRequest(
            name="Rahul Verma",
            email="not-an-email",
            password="ValidPassword123",
        )


def test_register_request_short_password() -> None:
    """Test password below 8 characters raises ValidationError."""
    with pytest.raises(ValidationError):
        RegisterRequest(
            name="Rahul Verma",
            email="rahul@example.com",
            password="short",
        )


def test_comparison_request_validation() -> None:
    """Test ComparisonRequest schema."""
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    req = ComparisonRequest(property_ids=[id1, id2])
    assert len(req.property_ids) == 2

    # Empty list or invalid type
    with pytest.raises(ValidationError):
        ComparisonRequest(property_ids=["not-a-uuid"])  # type: ignore


def test_user_preference_request_validation() -> None:
    """Test UserPreferenceRequest negative budgets."""
    with pytest.raises(ValidationError):
        UserPreferenceRequest.model_validate({"budget_min": -100})

    pref = UserPreferenceRequest(
        budget_min=4000000,
        budget_max=9000000,
        bhk_preferences=[2, 3],
        lifestyle_priorities=["metro", "schools"],
    )
    assert pref.budget_min == 4000000
    assert pref.bhk_preferences == [2, 3]
