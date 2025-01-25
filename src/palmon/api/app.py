from fastapi import FastAPI, HTTPException, Depends
from palmon.database.models import AsyncSessionLocal as SessionLocal, Pokemon
from palmon.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from starlette_prometheus import metrics, PrometheusMiddleware
from prometheus_client import Counter, Histogram
from dotenv import load_dotenv
import time

# Create custom metrics
pokemon_requests = Counter(
    'pokemon_requests_total',
    'Total number of requests to Pokemon endpoints',
    ['endpoint', 'status']
)

request_duration = Histogram(
    'pokemon_request_duration_seconds',
    'Time spent processing Pokemon requests',
    ['endpoint']
)

app = FastAPI(
    title="PalMon API",
)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/pokemon")
async def get_pokemon_list(
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get a list of Pokemon with pagination."""
    start_time = time.time()
    try:
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(status_code=400, detail="Invalid page number")
        if limit < 1:
            raise HTTPException(status_code=400, detail="Invalid limit")
        if limit > 1000:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 1000")
            
        offset = (page - 1) * limit
        
        # Use async query
        stmt = select(Pokemon).offset(offset).limit(limit)
        result = await db.execute(stmt)
        pokemon_list = result.scalars().all()
        
        response = {
            "data": [pokemon.to_dict() for pokemon in pokemon_list],
            "meta": {
                "page": page,
                "limit": limit
            },
            "links": {
                "self": f"/api/pokemon?page={page}&limit={limit}",
                "next": f"/api/pokemon?page={page+1}&limit={limit}",
                "prev": f"/api/pokemon?page={page-1}&limit={limit}" if page > 1 else None
            }
        }
        pokemon_requests.labels(endpoint='/api/pokemon', status='200').inc()
        request_duration.labels(endpoint='/api/pokemon').observe(time.time() - start_time)
        return response
    except HTTPException:
        pokemon_requests.labels(endpoint='/api/pokemon', status='400').inc()
        raise
    except Exception as e:
        pokemon_requests.labels(endpoint='/api/pokemon', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pokemon/{pokemon_id}")
async def get_pokemon_by_id(
    pokemon_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific Pokemon by ID."""
    start_time = time.time()
    try:
        stmt = select(Pokemon).where(Pokemon.id == pokemon_id)
        result = await db.execute(stmt)
        pokemon = result.scalar_one_or_none()
        
        if pokemon is None:
            pokemon_requests.labels(endpoint='/api/pokemon/{id}', status='404').inc()
            raise HTTPException(status_code=404, detail="Pokemon not found")
        
        response = {
            "data": pokemon.to_dict(),
            "links": {
                "self": f"/api/pokemon/{pokemon_id}"
            }
        }
        pokemon_requests.labels(endpoint='/api/pokemon/{id}', status='200').inc()
        request_duration.labels(endpoint='/api/pokemon/{id}').observe(time.time() - start_time)
        return response
    except HTTPException:
        raise
    except Exception as e:
        pokemon_requests.labels(endpoint='/api/pokemon/{id}', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    load_dotenv()
    uvicorn.run(app, host="0.0.0.0", port=8000)