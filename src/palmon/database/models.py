import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class Pokemon(Base):
    __tablename__ = 'pokemon'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    height = Column(Float)
    weight = Column(Float)
    types = Column(String)  # Stored as comma-separated values
    image_url = Column(String)
    base_experience = Column(Integer)
    
    def to_dict(self):
        return {
            "type": "pokemon",
            "id": str(self.id),
            "attributes": {
                "name": self.name,
                "height": self.height,
                "weight": self.weight,
                "types": self.types.split(',') if self.types else [],
                "image_url": self.image_url,
                "base_experience": self.base_experience
            }
        }

# Use aiosqlite for async SQLite support
database_path = os.getenv('DATABASE_PATH', 'pokemon.db')
engine = create_async_engine(f'sqlite+aiosqlite:///{database_path}', echo=True)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 