import asyncio
import httpx
import logging
import traceback
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from palmon.database.models import Pokemon, AsyncSessionLocal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokemonScraper:
    def __init__(self, session: AsyncSession = None):
        self.base_url = "https://pokeapi.co/api/v2"
        self._db = session

    @property
    async def session(self) -> AsyncSession:
        if self._db is None:
            self._db = AsyncSessionLocal()
        return self._db

    async def fetch_pokemon(self, client, pokemon_id):
        try:
            response = await client.get(f"{self.base_url}/pokemon/{pokemon_id}")
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.warning(f"Error: Got status code {response.status_code} for Pokémon ID {pokemon_id}")
                return None
            
            return response.json()
        except Exception as e:
            logger.error(
                f"Error fetching Pokémon ID {pokemon_id}: {str(e)}\n{traceback.format_exc()}"
            )
            return None

    async def scrape_pokemon(self, limit=151):
        db = await self.session

        async with httpx.AsyncClient() as client:
            tasks = [
                self.fetch_pokemon(client, pokemon_id)
                for pokemon_id in range(1, limit + 1)
            ]
            results = await asyncio.gather(*tasks)

            for data in results:
                if data is None:
                    continue

                pokemon = Pokemon(
                    id=data['id'],
                    name=data['name'],
                    height=data['height'] / 10,
                    weight=data['weight'] / 10,
                    types=','.join(t['type']['name'] for t in data['types']),
                    image_url=data['sprites']['front_default'],
                    base_experience=data['base_experience']
                )

                # Check for existing pokemon using async query
                stmt = select(Pokemon).where(Pokemon.id == pokemon.id)
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    await db.delete(existing)

                db.add(pokemon)
                await db.commit()
                logger.info(f"Scraped Pokémon: {pokemon.name}")

        return True

if __name__ == "__main__":
    async def main():
        scraper = PokemonScraper()
        await scraper.scrape_pokemon()

    asyncio.run(main()) 