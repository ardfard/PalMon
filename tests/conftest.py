import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from palmon.database.models import Base, Pokemon

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    return create_async_engine(TEST_DATABASE_URL, echo=True)

@pytest.fixture(autouse=True)
async def setup_database(engine):
    """Set up the test database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(engine):
    """Create a test database session."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def sample_pokemon(db_session):
    """Create sample Pokemon data."""
    pokemon1 = Pokemon(
        id=1,
        name="bulbasaur",
        height=0.7,
        weight=6.9,
        types="grass,poison",
        image_url="https://example.com/bulbasaur.png",
        base_experience=64
    )
    pokemon2 = Pokemon(
        id=2,
        name="ivysaur",
        height=1.0,
        weight=13.0,
        types="grass,poison",
        image_url="https://example.com/ivysaur.png",
        base_experience=142
    )
    db_session.add_all([pokemon1, pokemon2])
    await db_session.commit()
    return [pokemon1, pokemon2] 