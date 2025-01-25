import pytest
from palmon.database.models import Pokemon
from sqlalchemy import select
from sqlalchemy.sql import text

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


@pytest.mark.asyncio
async def test_pokemon_model_relationships(db_session):
    """Test Pokemon model relationships and cascades."""
    pokemon = Pokemon(
        id=2000,
        name="test_relations",
        height=1.0,
        weight=1.0,
        types="fire",
        image_url="test.png",
        base_experience=100
    )
    
    db_session.add(pokemon)
    await db_session.commit()
    
    # Test deletion
    await db_session.delete(pokemon)
    await db_session.commit()
    
    result = await db_session.execute(
        select(Pokemon).where(Pokemon.id == 2000)
    )
    assert result.first() is None

@pytest.mark.asyncio
async def test_init_db():
    """Test database initialization."""
    from palmon.database.models import init_db, engine, Base
    
    # Drop all tables first
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Test initialization
    await init_db()
    
    # Verify tables were created
    async with engine.begin() as conn:
        result = await conn.run_sync(lambda sync_conn: 
            sync_conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        )
        tables = [row[0] for row in result]
        assert "pokemon" in tables

@pytest.mark.asyncio
async def test_get_db():
    """Test database session factory."""
    from palmon.database.models import get_db
    
    async for session in get_db():
        assert session is not None
        # Test session can execute queries
        result = await session.execute(select(Pokemon))
        assert result is not None
        break 