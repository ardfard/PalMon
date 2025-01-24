from fastapi import FastAPI, HTTPException
from database.models import SessionLocal, Pokemon
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pokemon API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/pokemon")
async def get_pokemon(page: int = 1, limit: int = 10):
    session = SessionLocal()
    try:
        offset = (page - 1) * limit
        pokemon_list = session.query(Pokemon).offset(offset).limit(limit).all()
        total = session.query(Pokemon).count()
        
        return {
            "data": [pokemon.to_dict() for pokemon in pokemon_list],
            "meta": {
                "total": total,
                "page": page,
                "limit": limit
            },
            "links": {
                "self": f"/api/pokemon?page={page}&limit={limit}",
                "first": f"/api/pokemon?page=1&limit={limit}",
                "last": f"/api/pokemon?page={-(-total//limit)}&limit={limit}",
                "next": f"/api/pokemon?page={page+1}&limit={limit}" if offset + limit < total else None,
                "prev": f"/api/pokemon?page={page-1}&limit={limit}" if page > 1 else None
            }
        }
    finally:
        session.close()

@app.get("/api/pokemon/{pokemon_id}")
async def get_pokemon_by_id(pokemon_id: int):
    session = SessionLocal()
    try:
        pokemon = session.query(Pokemon).filter_by(id=pokemon_id).first()
        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokemon not found")
        
        return {
            "data": pokemon.to_dict(),
            "links": {
                "self": f"/api/pokemon/{pokemon_id}"
            }
        }
    finally:
        session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 