import pytest
from fastapi.testclient import TestClient
from palmon.api.app import app
from palmon.database.models import SessionLocal, Pokemon
from palmon.database import get_db
from pprint import pprint

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_dependency(test_db):
    """Automatically override database dependency for all tests."""
    app.dependency_overrides[get_db] = lambda: test_db
    yield
    app.dependency_overrides = {}

def test_get_pokemon_list(sample_pokemon):
    """Test getting list of Pokemon."""
    response = client.get("/api/pokemon")
    assert response.status_code == 200
    
    data = response.json()
    pprint(data)
    assert "data" in data
    assert len(data["data"]) == 2  # We expect 2 Pokemon from our sample data
    assert data["meta"]["total"] == 2
    assert data["links"]["self"] == "/api/pokemon?page=1&limit=10"

def test_get_pokemon_pagination(sample_pokemon):
    """Test Pokemon list pagination."""
    response = client.get("/api/pokemon?page=1&limit=1")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["data"]) == 1
    assert data["meta"]["page"] == 1
    assert data["meta"]["limit"] == 1
    assert data["links"]["next"] is not None

def test_get_pokemon_by_id(sample_pokemon):
    """Test getting a specific Pokemon."""
    response = client.get("/api/pokemon/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["data"]["attributes"]["name"] == "bulbasaur"

def test_get_nonexistent_pokemon():
    """Test getting a Pokemon that doesn't exist."""
    response = client.get("/api/pokemon/999")
    assert response.status_code == 404

def test_get_pokemon_list_error(test_db, monkeypatch):
    """Test error handling in get_pokemon list."""
    def mock_query(*args, **kwargs):
        raise Exception("Database error")
    
    # Patch the query method to raise an exception
    monkeypatch.setattr(test_db, "query", mock_query)
    
    response = client.get("/api/pokemon")
    assert response.status_code == 500

def test_get_pokemon_by_id_error(test_db, monkeypatch):
    """Test error handling in get_pokemon_by_id."""
    def mock_query(*args, **kwargs):
        raise Exception("Database error")
    
    # Patch the query method to raise an exception
    monkeypatch.setattr(test_db, "query", mock_query)
    
    response = client.get("/api/pokemon/1")
    assert response.status_code == 500

def test_metrics_endpoint():
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "pokemon_requests_total" in response.text

