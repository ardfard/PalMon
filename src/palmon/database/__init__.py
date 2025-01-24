"""Database package."""
from palmon.database.models import SessionLocal

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 