import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

database_path = os.getenv('DATABASE_PATH', 'pokemon.db')
engine = create_engine(f'sqlite:///{database_path}')
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine) 