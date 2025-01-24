import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pokemon_api.database.models import Base, Pokemon

@pytest.fixture
def test_db():
    """Create a test database."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    return TestingSessionLocal()

@pytest.fixture
def sample_pokemon(test_db):
    """Create sample Pokemon data."""
    pokemon_data = [
        {
            "id": 1,
            "name": "bulbasaur",
            "height": 0.7,
            "weight": 6.9,
            "types": "grass,poison",
            "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
            "base_experience": 64
        },
        {
            "id": 4,
            "name": "charmander",
            "height": 0.6,
            "weight": 8.5,
            "types": "fire",
            "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png",
            "base_experience": 62
        }
    ]
    
    for data in pokemon_data:
        pokemon = Pokemon(**data)
        test_db.add(pokemon)
    test_db.commit()
    
    return pokemon_data 