import pytest
from palmon.database import get_db

@pytest.mark.asyncio
async def test_get_db():
    """Test database session management."""
    async for db in get_db():
        assert db is not None
        await db.close()
        break  # We only need to test one iteration 