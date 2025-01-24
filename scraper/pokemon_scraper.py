import requests
from database.models import Pokemon, SessionLocal

class PokemonScraper:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.session = SessionLocal()

    def scrape_pokemon(self, limit=151):  # Default to original 151 Pokemon
        try:
            for pokemon_id in range(1, limit + 1):
                response = requests.get(f"{self.base_url}/pokemon/{pokemon_id}")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Create Pokemon object
                    pokemon = Pokemon(
                        id=data['id'],
                        name=data['name'],
                        height=data['height'] / 10,  # Convert to meters
                        weight=data['weight'] / 10,  # Convert to kilograms
                        types=','.join([t['type']['name'] for t in data['types']]),
                        image_url=data['sprites']['front_default'],
                        base_experience=data['base_experience']
                    )
                    
                    # Add to database
                    existing = self.session.query(Pokemon).filter_by(id=pokemon.id).first()
                    if existing:
                        self.session.delete(existing)
                    
                    self.session.add(pokemon)
                    self.session.commit()
                    print(f"Scraped Pokemon: {pokemon.name}")
                    
        except Exception as e:
            print(f"Error scraping Pokemon: {str(e)}")
            self.session.rollback()
        finally:
            self.session.close()

if __name__ == "__main__":
    scraper = PokemonScraper()
    scraper.scrape_pokemon() 