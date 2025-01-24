import pytest
from unittest.mock import Mock, patch
from pokemon_api.scraper.pokemon_scraper import PokemonScraper

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
    scraper = PokemonScraper()
    assert scraper.base_url == "https://pokeapi.co/api/v2"
    assert scraper.session is not None

@patch('requests.get')
def test_scrape_pokemon_success(mock_get, test_db, mock_response):
    """Test successful Pokemon scraping."""
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: mock_response
    )
    
    scraper = PokemonScraper()
    scraper.scrape_pokemon(limit=1)
    
    pokemon = test_db.query(Pokemon).first()
    assert pokemon is not None
    assert pokemon.name == "bulbasaur"
    assert pokemon.types == "grass,poison"

@patch('requests.get')
def test_scrape_pokemon_error(mock_get, test_db):
    """Test error handling during scraping."""
    mock_get.side_effect = Exception("API Error")
    
    scraper = PokemonScraper()
    scraper.scrape_pokemon(limit=1)
    
    # Should handle error gracefully
    pokemon_count = test_db.query(Pokemon).count()
    assert pokemon_count == 0 