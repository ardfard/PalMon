import pytest
from fastapi.testclient import TestClient
from palmon.api.app import app
from palmon.database.models import AsyncSessionLocal, Pokemon
from palmon.database import get_db
from sqlalchemy import select

client = TestClient(app=app)

@pytest.fixture(autouse=True)
async def override_dependency(db_session):
    """Automatically override database dependency for all tests."""
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_get_pokemon_list(sample_pokemon, db_session):
    """Test getting list of Pokemon."""
    response = client.get("/api/pokemon?page=1&limit=10")
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["attributes"]["name"] == "bulbasaur"

@pytest.mark.asyncio
async def test_get_pokemon_by_id(sample_pokemon, db_session):
    """Test getting a specific Pokemon by ID."""
    response = client.get("/api/pokemon/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["data"]["attributes"]["name"] == "bulbasaur"

@pytest.mark.asyncio
async def test_get_pokemon_by_id_not_found(db_session):
    """Test getting a non-existent Pokemon."""
    response = client.get("/api/pokemon/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_pokemon_by_id_error(db_session, monkeypatch):
    """Test error handling in get_pokemon_by_id."""
    async def mock_execute(*args, **kwargs):
        raise Exception("Database error")
    
    monkeypatch.setattr(db_session, "execute", mock_execute)
    
    response = client.get("/api/pokemon/1")
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "pokemon_requests_total" in response.text

