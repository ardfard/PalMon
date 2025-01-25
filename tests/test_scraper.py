import pytest
from palmon.scraper.pokemon_scraper import PokemonScraper
from palmon.database.models import Pokemon, init_db, AsyncSessionLocal
import httpx
import respx
from sqlalchemy import select

@pytest.fixture
async def test_db():
    """Create a test database session."""
    await init_db()
    async with AsyncSessionLocal() as session:
        yield session
        # Clean up
        await session.rollback()
        
@pytest.fixture
def mock_response():
    """Create a mock response for the Pokemon API."""
    return {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
        "sprites": {"front_default": "https://example.com/bulbasaur.png"},
        "base_experience": 64
    }

@pytest.mark.asyncio
async def test_scraper_initialization(db_session):
    """Test PokemonScraper initialization."""
    scraper = PokemonScraper(session=db_session)
    assert scraper.base_url == "https://pokeapi.co/api/v2"
    session = await scraper.session
    assert session is not None

@pytest.mark.asyncio
@respx.mock
async def test_fetch_pokemon_success(mock_response):
    """Test successful fetch of a Pokemon."""
    scraper = PokemonScraper()
    
    respx.get("https://pokeapi.co/api/v2/pokemon/1").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    
    async with httpx.AsyncClient() as client:
        data = await scraper.fetch_pokemon(client, 1)
    
    assert data is not None
    assert data['name'] == 'bulbasaur'
    assert data['id'] == 1

@pytest.mark.asyncio
@respx.mock
async def test_fetch_pokemon_non_200_response():
    """Test fetch_pokemon handling of non-200 response."""
    scraper = PokemonScraper()
    
    respx.get("https://pokeapi.co/api/v2/pokemon/1").mock(
        return_value=httpx.Response(404, json={"error": "Not found"})
    )
    
    async with httpx.AsyncClient() as client:
        data = await scraper.fetch_pokemon(client, 1)
    
    assert data is None

@pytest.mark.asyncio
@respx.mock
async def test_fetch_pokemon_exception():
    """Test fetch_pokemon handling of an exception."""
    scraper = PokemonScraper()
    
    respx.get("https://pokeapi.co/api/v2/pokemon/1").mock(
        side_effect=httpx.RequestError("Network Error")
    )
    
    async with httpx.AsyncClient() as client:
        data = await scraper.fetch_pokemon(client, 1)
    
    assert data is None

@pytest.mark.asyncio
@respx.mock
async def test_scrape_pokemon_success(mock_response, db_session):
    """Test successful Pokemon scraping."""
    scraper = PokemonScraper(session=db_session)
    
    respx.get("https://pokeapi.co/api/v2/pokemon/1").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    
    await scraper.scrape_pokemon(limit=1)
    
    # Use async query
    result = await db_session.execute(select(Pokemon))
    pokemon = result.scalar_one()
    assert pokemon is not None
    assert pokemon.name == "bulbasaur"
    assert pokemon.types == "grass,poison"

@pytest.mark.asyncio
@respx.mock
async def test_scrape_pokemon_update_existing(mock_response, db_session):
    """Test scraping when Pokemon already exists."""
    # First create an existing Pokemon
    existing_pokemon = Pokemon(
        id=1,
        name="old_name",
        height=1.0,
        weight=1.0,
        types="normal",
        image_url="old.png",
        base_experience=100
    )
    
    # Use async operations for setup
    db_session.add(existing_pokemon)
    await db_session.commit()
    
    respx.get("https://pokeapi.co/api/v2/pokemon/1").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    
    scraper = PokemonScraper(session=db_session)
    await scraper.scrape_pokemon(limit=1)
    
    # Use async query to check results
    result = await db_session.execute(select(Pokemon).where(Pokemon.id == 1))
    pokemon = result.scalar_one()
    assert pokemon.name == "bulbasaur"
    assert pokemon.types == "grass,poison"

@pytest.mark.asyncio
async def test_scraper_session_creation():
    """Test scraper session creation when no session is provided."""
    scraper = PokemonScraper()
    session = await scraper.session
    assert session is not None
    
    # Test session can execute queries
    result = await session.execute(select(Pokemon))
    assert result is not None