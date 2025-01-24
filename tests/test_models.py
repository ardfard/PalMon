import pytest
from pokemon_api.database.models import Pokemon

def test_pokemon_model_creation(test_db):
    """Test Pokemon model creation."""
    pokemon = Pokemon(
        id=1,
        name="bulbasaur",
        height=0.7,
        weight=6.9,
        types="grass,poison",
        image_url="https://example.com/bulbasaur.png",
        base_experience=64
    )
    
    test_db.add(pokemon)
    test_db.commit()
    
    saved_pokemon = test_db.query(Pokemon).first()
    assert saved_pokemon.name == "bulbasaur"
    assert saved_pokemon.types == "grass,poison"

def test_pokemon_to_dict(test_db, sample_pokemon):
    """Test Pokemon to_dict method."""
    pokemon = test_db.query(Pokemon).first()
    pokemon_dict = pokemon.to_dict()
    
    assert pokemon_dict["type"] == "pokemon"
    assert pokemon_dict["id"] == "1"
    assert pokemon_dict["attributes"]["name"] == "bulbasaur"
    assert "grass" in pokemon_dict["attributes"]["types"]
    assert "poison" in pokemon_dict["attributes"]["types"] 