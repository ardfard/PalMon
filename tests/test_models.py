import pytest
from palmon.database.models import Pokemon
from sqlalchemy import select

@pytest.mark.asyncio
async def test_pokemon_model_creation(db_session):
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
    
    db_session.add(pokemon)
    await db_session.commit()
    
    # Query specifically for the Pokemon we just created
    result = await db_session.execute(
        select(Pokemon).where(Pokemon.id == 1)
    )
    saved_pokemon = result.scalar_one()
    assert saved_pokemon.name == "bulbasaur"
    assert saved_pokemon.types == "grass,poison"

@pytest.mark.asyncio
async def test_pokemon_to_dict(db_session, sample_pokemon):
    """Test Pokemon to_dict method."""
    # Query for a specific Pokemon (first one from sample data)
    result = await db_session.execute(
        select(Pokemon).where(Pokemon.id == 1)
    )
    pokemon = result.scalar_one()
    pokemon_dict = pokemon.to_dict()
    
    assert pokemon_dict["type"] == "pokemon"
    assert pokemon_dict["id"] == "1"
    assert pokemon_dict["attributes"]["name"] == "bulbasaur"
    assert "grass" in pokemon_dict["attributes"]["types"]
    assert "poison" in pokemon_dict["attributes"]["types"]

@pytest.mark.asyncio
async def test_pokemon_to_dict_empty_types(db_session):
    """Test Pokemon to_dict method with empty types."""
    pokemon = Pokemon(
        id=999,  # Use a different ID to avoid conflicts
        name="test",
        height=1.0,
        weight=1.0,
        types=None,  # Test empty types
        image_url="test.png",
        base_experience=100
    )
    
    db_session.add(pokemon)
    await db_session.commit()
    
    # Query for the specific Pokemon we just created
    result = await db_session.execute(
        select(Pokemon).where(Pokemon.id == 999)
    )
    saved_pokemon = result.scalar_one()
    result = saved_pokemon.to_dict()
    assert result["attributes"]["types"] == [] 