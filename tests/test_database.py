from palmon.database import get_db

def test_get_db():
    """Test database session management."""
    db = next(get_db())
    assert db is not None
    db.close() 