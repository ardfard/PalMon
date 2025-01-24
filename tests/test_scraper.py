import pytest
from unittest.mock import Mock, patch
from palmon.scraper.pokemon_scraper import PokemonScraper
from palmon.database.models import Pokemon

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

def test_scraper_initialization(test_db):
    """Test PokemonScraper initialization."""
    scraper = PokemonScraper(session=test_db)
    assert scraper.base_url == "https://pokeapi.co/api/v2"
    assert scraper.session is not None

@patch('requests.get')
def test_scrape_pokemon_success(mock_get, test_db, mock_response):
    """Test successful Pokemon scraping."""
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: mock_response
    )
    
    scraper = PokemonScraper(session=test_db)
    scraper.scrape_pokemon(limit=1)
    
    pokemon = test_db.query(Pokemon).first()
    assert pokemon is not None
    assert pokemon.name == "bulbasaur"
    assert pokemon.types == "grass,poison"

@patch('requests.get')
def test_scrape_pokemon_error(mock_get, test_db):
    """Test error handling during scraping."""
    mock_get.side_effect = Exception("API Error")
    
    scraper = PokemonScraper(session=test_db)
    result = scraper.scrape_pokemon(limit=1)
    
    # Should handle error gracefully
    assert result is False  # Check that scraping failed
    pokemon_count = test_db.query(Pokemon).count()
    assert pokemon_count == 0 

@patch('requests.get')
def test_scrape_pokemon_non_200_response(mock_get, test_db):
    """Test scraper handling of non-200 response."""
    mock_get.return_value = Mock(
        status_code=404  # Simulate a not found response
    )
    
    scraper = PokemonScraper(session=test_db)
    result = scraper.scrape_pokemon(limit=1)
    
    assert result is False  # Should return False on failure
    pokemon_count = test_db.query(Pokemon).count()
    assert pokemon_count == 0  # No Pokemon should be added

@patch('requests.get')
def test_scrape_pokemon_update_existing(mock_get, test_db, mock_response):
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
    test_db.add(existing_pokemon)
    test_db.commit()
    
    # Now try to scrape the same Pokemon
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: mock_response
    )
    
    scraper = PokemonScraper(session=test_db)
    result = scraper.scrape_pokemon(limit=1)
    
    assert result is True
    pokemon = test_db.query(Pokemon).first()
    assert pokemon.name == "bulbasaur"  # Should be updated to new name
    assert pokemon.types == "grass,poison"  # Should be updated to new types