import pytest
from fastapi.testclient import TestClient
from pokemon_api.api.app import app
from pokemon_api.database.models import SessionLocal, Pokemon

client = TestClient(app)

def test_get_pokemon_list(sample_pokemon):
    """Test getting list of Pokemon."""
    response = client.get("/api/pokemon")
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2
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