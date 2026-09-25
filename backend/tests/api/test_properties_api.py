"""API integration tests for properties endpoints and nested sub-routes."""

import uuid
from fastapi.testclient import TestClient
from datasage.models.property import Property


def test_search_properties(client: TestClient) -> None:
    """Test searching properties returns paginated response with data list."""
    response = client.get("/api/v1/properties?bhk=3&limit=10")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1


def test_get_property_detail(client: TestClient, mock_property: Property) -> None:
    """Test getting single property details."""
    response = client.get(f"/api/v1/properties/{mock_property.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(mock_property.id)
    assert data["title"] == mock_property.title
    assert data["bhk"] == 3
    assert data["locality"]["name"] == "Sector 75"


def test_get_property_detail_not_found(client: TestClient) -> None:
    """Test 404 response for non-existent property UUID."""
    random_uuid = uuid.uuid4()
    response = client.get(f"/api/v1/properties/{random_uuid}")
    assert response.status_code == 404


def test_get_property_valuation_subroute(client: TestClient, mock_property: Property) -> None:
    """Test nested GET /api/v1/properties/{id}/valuation subroute."""
    response = client.get(f"/api/v1/properties/{mock_property.id}/valuation")
    assert response.status_code == 200
    data = response.json()
    assert data["property_id"] == str(mock_property.id)
    assert "predicted_value" in data
    assert "pricing_classification" in data


def test_get_property_location_subroute(client: TestClient, mock_property: Property) -> None:
    """Test nested GET /api/v1/properties/{id}/location subroute."""
    response = client.get(f"/api/v1/properties/{mock_property.id}/location")
    assert response.status_code == 200
    data = response.json()
    assert "composite_score" in data
    assert "sub_scores" in data


def test_get_property_investment_subroute(client: TestClient, mock_property: Property) -> None:
    """Test nested GET /api/v1/properties/{id}/investment subroute."""
    response = client.get(f"/api/v1/properties/{mock_property.id}/investment")
    assert response.status_code == 200
    data = response.json()
    assert "investment_score" in data
    assert "gross_rental_yield_pct" in data


def test_get_property_similar_subroute(client: TestClient, mock_property: Property) -> None:
    """Test nested GET /api/v1/properties/{id}/similar subroute."""
    response = client.get(f"/api/v1/properties/{mock_property.id}/similar?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
