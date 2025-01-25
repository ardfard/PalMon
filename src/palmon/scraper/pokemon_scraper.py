import asyncio
import httpx
import logging
import traceback
import os
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from palmon.database.models import Pokemon, AsyncSessionLocal, init_db

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

    async def scrape_pokemon(self, limit=None, concurrency=None):
        # Use environment variables if parameters not provided

        sem = asyncio.Semaphore(concurrency)
        client_pool = []

        logger.info(f"Starting Pokemon scraper with limit={limit}, concurrency={concurrency}")

        # Create a pool of clients
        for _ in range(concurrency):
            client = httpx.AsyncClient(
                limits=httpx.Limits(max_keepalive_connections=1),
                timeout=httpx.Timeout(10.0, connect=5.0)
            )
            client_pool.append(client)

        try:
            async def process_pokemon(pokemon_id):
                # Use provided session if available, otherwise create new one
                if self._db is not None:
                    db = self._db
                else:
                    db = AsyncSessionLocal()

                async with sem:
                    # Get a client from the pool
                    client = client_pool[pokemon_id % concurrency]
                    try:
                        data = await self.fetch_pokemon(client, pokemon_id)
                        if data is None:
                            return

                        pokemon = Pokemon(
                            id=data['id'],
                            name=data['name'],
                            height=data['height'] / 10,
                            weight=data['weight'] / 10,
                            types=','.join(t['type']['name'] for t in data['types']),
                            image_url=data['sprites']['front_default'],
                            base_experience=data['base_experience']
                        )

                        stmt = select(Pokemon).where(Pokemon.id == pokemon.id)
                        result = await db.execute(stmt)
                        existing = result.scalar_one_or_none()

                        if existing:
                            await db.delete(existing)

                        db.add(pokemon)
                        await db.commit()
                        logger.info(f"Scraped Pokémon: {pokemon.name}")

                    except Exception as e:
                        await db.rollback()  # Rollback on error
                        logger.error(f"Error processing Pokemon {pokemon_id}: {str(e)}")
                        raise  # Re-raise the exception for the test to catch

            # Create and run tasks
            tasks = (
                process_pokemon(pokemon_id)
                for pokemon_id in range(1, limit + 1)
            )
            await asyncio.gather(*tasks)

        finally:
            # Clean up clients
            for client in client_pool:
                await client.aclose()

        return True

if __name__ == "__main__":
    async def main():
        # Load environment variables
        load_dotenv()

        # Get configuration from environment variables
        scrapping_limit = int(os.getenv('POKEMON_SCRAPER_LIMIT', 151))
        scrapping_concurrency = int(os.getenv('POKEMON_SCRAPER_CONCURRENCY', 10))


        await init_db()
        scraper = PokemonScraper()
        await scraper.scrape_pokemon(scrapping_limit, scrapping_concurrency)

    asyncio.run(main()) 