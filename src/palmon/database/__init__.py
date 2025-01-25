"""Database package."""
from palmon.database.models import AsyncSessionLocal as SessionLocal
from palmon.database.models import Base, init_db

async def get_db():
    """Dependency for getting DB sessions."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 