import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from pokemon_api.database.models import Base, Pokemon

@pytest.fixture(scope="session")
def engine():
    """Create the test database engine."""
    engine = create_engine('sqlite:///:memory:', connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)  # Create tables once for the test session
    return engine

@pytest.fixture(scope="function")
def test_db(engine):
    """Create a fresh test database for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    db = TestingSessionLocal()

    yield db

    db.close()
    transaction.rollback()
    connection.close()

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