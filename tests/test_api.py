import pytest
from fastapi.testclient import TestClient
from palmon.api.app import app
from palmon.database.models import AsyncSessionLocal, Pokemon, Base
from palmon.database import get_db
from sqlalchemy import select, delete
from httpx import AsyncClient

client = TestClient(app=app)

@pytest.fixture(autouse=True)
async def override_dependency(db_session):
    """Automatically override database dependency for all tests."""
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides = {}

@pytest.fixture
async def clean_db(db_session):
    """Clean the database before and after each test."""
    # Clean before test
    await db_session.execute(delete(Pokemon))
    await db_session.commit()
    
    yield db_session
    
    # Clean after test
    await db_session.execute(delete(Pokemon))
    await db_session.commit()

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
    # Ensure sample Pokemon is in database
    result = await db_session.execute(select(Pokemon).where(Pokemon.id == 1))
    pokemon = result.scalar_one_or_none()
    if not pokemon:
        db_session.add(sample_pokemon)
        await db_session.commit()
    
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

@pytest.mark.asyncio
async def test_get_pokemon_list_error(db_session, monkeypatch):
    """Test error handling in get_pokemon_list."""
    async def mock_execute(*args, **kwargs):
        raise Exception("Database error")
    
    monkeypatch.setattr(db_session, "execute", mock_execute)
    
    response = client.get("/api/pokemon?page=1&limit=10")
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_pokemon_list_pagination(clean_db):
    """Test pagination in get_pokemon_list."""
    # Create test data
    pokemon_data = [
        Pokemon(
            id=1,
            name="bulbasaur",
            height=0.7,
            weight=6.9,
            types="grass,poison",
            image_url="https://example.com/bulbasaur.png",
            base_experience=64
        ),
        Pokemon(
            id=2,
            name="ivysaur",
            height=1.0,
            weight=13.0,
            types="grass,poison",
            image_url="https://example.com/ivysaur.png",
            base_experience=142
        ),
        Pokemon(
            id=3,
            name="venusaur",
            height=2.0,
            weight=100.0,
            types="grass,poison",
            image_url="https://example.com/venusaur.png",
            base_experience=236
        )
    ]
    
    for pokemon in pokemon_data:
        clean_db.add(pokemon)
    await clean_db.commit()

    # Test first page
    response = client.get("/api/pokemon?page=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["meta"]["page"] == 1
    assert data["meta"]["limit"] == 1
    assert data["links"]["prev"] is None
    assert "page=2" in data["links"]["next"]

    # Test second page
    response = client.get("/api/pokemon?page=2&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["meta"]["page"] == 2
    assert "page=1" in data["links"]["prev"]
    assert "page=3" in data["links"]["next"]

@pytest.mark.asyncio
async def test_get_pokemon_list_empty(db_session):
    """Test get_pokemon_list with empty database."""
    response = client.get("/api/pokemon?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 0

@pytest.mark.asyncio
async def test_get_pokemon_by_id_validation(db_session):
    """Test input validation for get_pokemon_by_id."""
    response = client.get("/api/pokemon/0")  # Invalid ID
    assert response.status_code == 404

    response = client.get("/api/pokemon/-1")  # Negative ID
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_metrics_content():
    """Test metrics endpoint content."""
    # Make some requests to generate metrics
    client.get("/api/pokemon/1")
    client.get("/api/pokemon/999")
    
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    
    # Check for specific metrics
    assert 'pokemon_requests_total{endpoint="/api/pokemon/{id}",status="404"}' in content
    assert 'pokemon_request_duration_seconds' in content

@pytest.mark.asyncio
async def test_get_pokemon_list_with_invalid_page(db_session):
    """Test get_pokemon_list with invalid page parameter."""
    response = client.get("/api/pokemon?page=0&limit=10")  # Invalid page
    assert response.status_code == 400
    assert "Invalid page number" in response.json()["detail"]

    response = client.get("/api/pokemon?page=-1&limit=10")  # Negative page
    assert response.status_code == 400
    assert "Invalid page number" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_pokemon_list_with_invalid_limit(db_session):
    """Test get_pokemon_list with invalid limit parameter."""
    response = client.get("/api/pokemon?page=1&limit=0")  # Invalid limit
    assert response.status_code == 400
    assert "Invalid limit" in response.json()["detail"]

    response = client.get("/api/pokemon?page=1&limit=-10")  # Negative limit
    assert response.status_code == 400
    assert "Invalid limit" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_pokemon_list_with_large_limit(db_session):
    """Test get_pokemon_list with very large limit."""
    response = client.get("/api/pokemon?page=1&limit=1001")  # Exceeds max limit
    assert response.status_code == 400
    assert "Limit cannot exceed" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_pokemon_by_id_with_string_id(db_session):
    """Test get_pokemon_by_id with non-numeric ID."""
    response = client.get("/api/pokemon/abc")  # Non-numeric ID
    assert response.status_code == 422  # FastAPI validation error

@pytest.mark.asyncio
async def test_metrics_detailed(clean_db):
    """Test detailed metrics recording."""
    # Create a Pokemon for testing
    pokemon = Pokemon(
        id=1,
        name="test_pokemon",
        height=1.0,
        weight=1.0,
        types="test",
        image_url="test.png",
        base_experience=100
    )
    clean_db.add(pokemon)
    await clean_db.commit()

    # Generate various response types
    client.get("/api/pokemon/1")  # 200 response
    client.get("/api/pokemon/999")  # 404 response
    client.get("/api/pokemon?page=1&limit=10")  # List endpoint
    
    response = client.get("/metrics")
    content = response.text
    
    # Check for specific metric types
    assert 'pokemon_requests_total{endpoint="/api/pokemon",status="200"}' in content
    assert 'pokemon_requests_total{endpoint="/api/pokemon/{id}",status="200"}' in content
    assert 'pokemon_requests_total{endpoint="/api/pokemon/{id}",status="404"}' in content
    assert 'pokemon_request_duration_seconds_bucket' in content
    assert 'pokemon_request_duration_seconds_count' in content
    assert 'pokemon_request_duration_seconds_sum' in content

@pytest.mark.asyncio
async def test_get_pokemon_by_id_database_error(db_session, monkeypatch):
    """Test database error handling in get_pokemon_by_id."""
    async def mock_execute(*args, **kwargs):
        raise Exception("Database connection error")
    
    monkeypatch.setattr(db_session, "execute", mock_execute)
    response = client.get("/api/pokemon/1")
    
    assert response.status_code == 500
    assert "Database connection error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_pokemon_by_id_metrics(clean_db):
    """Test metrics recording for get_pokemon_by_id endpoint."""
    # Create test Pokemon
    pokemon = Pokemon(
        id=1,
        name="test_pokemon",
        height=1.0,
        weight=1.0,
        types="test",
        image_url="test.png",
        base_experience=100
    )
    clean_db.add(pokemon)
    await clean_db.commit()

    # Test successful request
    response = client.get("/api/pokemon/1")
    assert response.status_code == 200

    # Test not found request
    response = client.get("/api/pokemon/999")
    assert response.status_code == 404

    # Test error request
    async def mock_execute(*args, **kwargs):
        raise Exception("Test error")
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr(clean_db, "execute", mock_execute)
        response = client.get("/api/pokemon/1")
        assert response.status_code == 500

    # Check metrics
    metrics_response = client.get("/metrics")
    metrics_content = metrics_response.text

    # Verify all status codes are recorded
    assert 'pokemon_requests_total{endpoint="/api/pokemon/{id}",status="200"}' in metrics_content
    assert 'pokemon_requests_total{endpoint="/api/pokemon/{id}",status="404"}' in metrics_content
    assert 'pokemon_requests_total{endpoint="/api/pokemon/{id}",status="500"}' in metrics_content

    # Verify duration metrics
    assert 'pokemon_request_duration_seconds_bucket{endpoint="/api/pokemon/{id}"' in metrics_content
    assert 'pokemon_request_duration_seconds_sum{endpoint="/api/pokemon/{id}"' in metrics_content
    assert 'pokemon_request_duration_seconds_count{endpoint="/api/pokemon/{id}"' in metrics_content


@pytest.mark.asyncio
async def test_error_handling_chain(clean_db):
    """Test error handling chain and metrics recording."""
    # Test database error propagation
    async def mock_execute(*args, **kwargs):
        raise Exception("Database error")
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr(clean_db, "execute", mock_execute)
        
        # Test list endpoint
        response = client.get("/api/pokemon?page=1&limit=10")
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]
        
        # Test detail endpoint
        response = client.get("/api/pokemon/1")
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]

    # Verify error metrics
    metrics_response = client.get("/metrics")
    metrics_content = metrics_response.text
    
    assert 'pokemon_requests_total{endpoint="/api/pokemon",status="500"}' in metrics_content
    assert 'pokemon_requests_total{endpoint="/api/pokemon/{id}",status="500"}' in metrics_content
