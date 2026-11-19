"""Unit tests for PropertyService and property search/detail logic."""

import uuid
from unittest.mock import AsyncMock

import pytest

from datasage.core.exceptions import NotFoundError
from datasage.models.property import Property
from datasage.models.reference import Locality
from datasage.services.property_service import PropertyService


@pytest.mark.asyncio
async def test_get_property_detail_success(mock_property: Property, mock_locality: Locality) -> None:
    """Test retrieving full property detail by ID."""
    session = AsyncMock()
    service = PropertyService(session)

    service.property_repo.get_by_id = AsyncMock(return_value=mock_property)
    service.locality_repo.get_by_id = AsyncMock(return_value=mock_locality)

    detail = await service.get_detail(str(mock_property.id))

    assert detail.id == str(mock_property.id)
    assert detail.title == mock_property.title
    assert detail.bhk == 3
    assert detail.area_sqft == 1500.0
    assert detail.listing_price == 6500000
    assert detail.locality.name == "Sector 75"
    assert detail.location is not None
    assert detail.location.pin_code == "201301"
    assert len(detail.images) == 1


@pytest.mark.asyncio
async def test_get_property_detail_invalid_uuid() -> None:
    """Test get_detail with invalid UUID format raises NotFoundError."""
    session = AsyncMock()
    service = PropertyService(session)

    with pytest.raises(NotFoundError):
        await service.get_detail("not-a-valid-uuid")


@pytest.mark.asyncio
async def test_get_similar_properties(mock_property: Property, mock_locality: Locality) -> None:
    """Test retrieving similar properties."""
    similar_prop = Property(
        id=uuid.UUID("55555555-5555-5555-5555-555555555555"),
        city_id=1,
        locality_id=1,
        title="3 BHK Premium Apartment in Sector 75, Noida",
        property_type="apartment",
        bhk=3,
        area_sqft=1450.0,
        listing_price=6200000,
        cached_location_score=81.0,
        is_active=True,
    )
    similar_prop.images = []

    session = AsyncMock()
    service = PropertyService(session)

    service.property_repo.get_by_id = AsyncMock(return_value=mock_property)
    service.property_repo.search = AsyncMock(return_value=([similar_prop], None, 1))
    service.locality_repo.get_by_id = AsyncMock(return_value=mock_locality)

    similar_list = await service.get_similar(str(mock_property.id), limit=3)

    assert len(similar_list) == 1
    assert similar_list[0].id == str(similar_prop.id)
    assert similar_list[0].bhk == 3
    assert similar_list[0].listing_price == 6200000
