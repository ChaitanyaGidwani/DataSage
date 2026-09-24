"""Shared test fixtures for DataSage backend test suite."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from datasage.core.database import get_session
from datasage.core.security import create_access_token, hash_password
from datasage.main import app
from datasage.models.property import Property, PropertyImage
from datasage.models.reference import City, Locality
from datasage.models.user import User, UserPreference
from datasage.models.location import PropertyLocation
from datasage.models.valuation import ValuationPrediction, ModelVersion


@pytest.fixture
def mock_city() -> City:
    """Mock city reference model."""
    city = City(
        id=1,
        name="Noida",
        state="Uttar Pradesh",
        is_active=True,
    )
    return city


@pytest.fixture
def mock_locality(mock_city: City) -> Locality:
    """Mock locality reference model."""
    locality = Locality(
        id=1,
        city_id=1,
        name="Sector 75",
        slug="sector-75-noida",
        centroid_lat=28.5710,
        centroid_lng=77.3900,
        avg_price_per_sqft=7200.0,
        price_trend_1y_pct=12.5,
        price_trend_3y_pct=32.0,
    )
    locality.city = mock_city
    return locality


@pytest.fixture
def mock_property(mock_locality: Locality, mock_city: City) -> Property:
    """Mock property model with images and location."""
    prop_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    prop = Property(
        id=prop_id,
        city_id=1,
        locality_id=1,
        title="3 BHK Luxury Apartment in Sector 75, Noida",
        property_type="apartment",
        bhk=3,
        area_sqft=1500.0,
        listing_price=6500000,
        floor_number=6,
        total_floors=18,
        facing="east",
        construction_year=2021,
        furnishing="semi_furnished",
        parking_count=1,
        balcony_count=2,
        bathroom_count=2,
        description="Spacious high-rise apartment with panoramic skyline view and modular kitchen.",
        data_source="seed",
        latitude=28.5710,
        longitude=77.3900,
        cached_location_score=82.0,
        is_active=True,
        listed_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        created_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )
    prop.locality = mock_locality
    prop.city = mock_city

    # Mock image
    img = PropertyImage(
        id=uuid.uuid4(),
        property_id=prop_id,
        url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00",
        display_order=0,
        is_primary=True,
    )
    prop.images = [img]

    # Mock location
    loc = PropertyLocation(
        id=uuid.uuid4(),
        property_id=prop_id,
        coordinates="POINT(77.3900 28.5710)",
        full_address="Tower 4, Golf Vista, Sector 75, Noida",
        pin_code="201301",
        location_score=82.0,
    )
    prop.location = loc
    return prop


@pytest.fixture
def mock_user() -> User:
    """Standard buyer user fixture."""
    user_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
    return User(
        id=user_id,
        name="Priya Sharma",
        email="priya@example.com",
        password_hash=hash_password("SecurePass1"),
        role="buyer",
        email_verified=True,
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_admin_user() -> User:
    """Admin user fixture."""
    user_id = uuid.UUID("33333333-3333-3333-3333-333333333333")
    return User(
        id=user_id,
        name="Admin User",
        email="admin@datasage.ai",
        password_hash=hash_password("AdminSecure2026"),
        role="admin",
        email_verified=True,
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def user_access_token(mock_user: User) -> str:
    """JWT access token for mock_user."""
    return create_access_token(
        user_id=str(mock_user.id),
        email=mock_user.email,
        role=mock_user.role,
    )


@pytest.fixture
def admin_access_token(mock_admin_user: User) -> str:
    """JWT access token for mock_admin_user."""
    return create_access_token(
        user_id=str(mock_admin_user.id),
        email=mock_admin_user.email,
        role=mock_admin_user.role,
    )


@pytest.fixture
def mock_user_preference(mock_user: User) -> UserPreference:
    """Mock user preferences fixture."""
    return UserPreference(
        id=uuid.UUID("88888888-8888-8888-8888-888888888888"),
        user_id=mock_user.id,
        budget_min=4500000,
        budget_max=8500000,
        bhk_preferences=[2, 3],
        preferred_locality_ids=[1],
        lifestyle_priorities=["metro", "schools", "parks"],
        property_type_preferences=["apartment"],
        commute_destination_lat=28.6139,
        commute_destination_lng=77.2090,
        commute_destination_label="Connaught Place",
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_session(
    mock_property: Property,
    mock_locality: Locality,
    mock_user: User,
    mock_admin_user: User,
    mock_user_preference: UserPreference,
) -> AsyncMock:
    """Mock AsyncSession for isolated database operations."""
    session = AsyncMock(spec=AsyncSession)

    async def mock_execute(query: Any, *args: Any, **kwargs: Any) -> MagicMock:
        mock_result = MagicMock()
        query_str = str(query).lower()
        empty_items: list[Any] = []

        params: dict[str, Any] = {}
        try:
            params = query.compile().params
        except Exception:
            pass
        param_values = list(params.values())

        # UserPreference query
        if "user_preference" in query_str:
            mock_result.scalar_one_or_none.return_value = mock_user_preference
            mock_result.scalars.return_value.all.return_value = [mock_user_preference]

        # User query
        elif "from \"user\"" in query_str or "from user" in query_str:
            if (
                mock_admin_user.id in param_values
                or "admin@datasage.ai" in param_values
                or str(mock_admin_user.id) in query_str
            ):
                mock_result.scalar_one_or_none.return_value = mock_admin_user
            else:
                mock_result.scalar_one_or_none.return_value = mock_user
            mock_result.scalar.return_value = 2

        # Count queries (e.g. for properties count in search or stats)
        elif "count(" in query_str:
            mock_result.scalar.return_value = 1
            mock_result.scalar_one_or_none.return_value = 1

        # Property detail query with specific ID (where property.id = ...)
        elif "from property" in query_str and "property.id =" in query_str:
            if mock_property.id in param_values or str(mock_property.id) in query_str:
                mock_result.scalar_one_or_none.return_value = mock_property
                mock_result.scalars.return_value.all.return_value = [mock_property]
            else:
                mock_result.scalar_one_or_none.return_value = None
                mock_result.scalars.return_value.all.return_value = empty_items

        # Property search list or multiple properties query
        elif "from property" in query_str:
            mock_result.scalars.return_value.all.return_value = [mock_property]
            mock_result.all.return_value = [(mock_property.id,)]

        # Locality query
        elif "from locality" in query_str:
            if 99999 in param_values or "99999" in str(param_values):
                mock_result.scalar_one_or_none.return_value = None
                mock_result.scalars.return_value.all.return_value = empty_items
            else:
                mock_result.scalar_one_or_none.return_value = mock_locality
                mock_result.scalars.return_value.all.return_value = [mock_locality]

        # City query
        elif "from city" in query_str:
            mock_result.scalar_one_or_none.return_value = mock_locality.city
            mock_result.scalars.return_value.all.return_value = [mock_locality.city]

        # Valuation prediction queries
        elif "valuation_prediction" in query_str:
            mock_result.scalar_one_or_none.return_value = None
            mock_result.scalars.return_value.all.return_value = empty_items
            mock_result.scalar.return_value = 1

        # Default fallback
        else:
            mock_result.scalar_one_or_none.return_value = None
            mock_result.scalars.return_value.all.return_value = empty_items
            mock_result.scalar.return_value = 0
            mock_result.all.return_value = empty_items

        return mock_result

    session.execute.side_effect = mock_execute
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    return session


@pytest.fixture
def client(mock_session: AsyncMock) -> Generator[TestClient, None, None]:
    """TestClient with database session dependency overridden."""
    app.dependency_overrides[get_session] = lambda: mock_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
