"""API integration tests for property comparison endpoints."""

import uuid

from fastapi.testclient import TestClient

from datasage.models.property import Property


def test_comparison_post_endpoint(client: TestClient, mock_property: Property) -> None:
    """Test POST /api/v1/comparison side-by-side comparison."""
    second_id = uuid.UUID("77777777-7777-7777-7777-777777777777")
    response = client.post(
        "/api/v1/comparison",
        json={"property_ids": [str(mock_property.id), str(second_id)]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "properties" in data
    assert "summary" in data


def test_comparison_get_query_param(client: TestClient, mock_property: Property) -> None:
    """Test GET /api/v1/comparison?ids=uuid1,uuid2."""
    second_id = uuid.UUID("77777777-7777-7777-7777-777777777777")
    response = client.get(f"/api/v1/comparison?ids={mock_property.id},{second_id}")
    assert response.status_code == 200
    data = response.json()
    assert "properties" in data
    assert "summary" in data


def test_comparison_invalid_uuid(client: TestClient) -> None:
    """Test GET /api/v1/comparison with malformed UUID returns 422."""
    response = client.get("/api/v1/comparison?ids=invalid-uuid-1,invalid-uuid-2")
    assert response.status_code == 422
