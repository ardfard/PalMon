from fastapi import FastAPI, HTTPException, Depends
from pokemon_api.database.models import SessionLocal, Pokemon
from pokemon_api.database import get_db
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from starlette_prometheus import metrics, PrometheusMiddleware
from prometheus_client import Counter, Histogram
import time

# Create custom metrics
pokemon_requests = Counter(
    'pokemon_requests_total',
    'Total number of requests to Pokemon endpoints',
    ['endpoint', 'status']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration in seconds',
    ['endpoint']
)

app = FastAPI(
    title="Pokemon API",
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
async def get_pokemon(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    start_time = time.time()
    try:
        offset = (page - 1) * limit
        pokemon_list = db.query(Pokemon).offset(offset).limit(limit).all()
        total = db.query(Pokemon).count()
        
        response = {
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
        pokemon_requests.labels(endpoint='/api/pokemon', status='200').inc()
        request_duration.labels(endpoint='/api/pokemon').observe(time.time() - start_time)
        return response
    except Exception as e:
        pokemon_requests.labels(endpoint='/api/pokemon', status='500').inc()
        raise

@app.get("/api/pokemon/{pokemon_id}")
async def get_pokemon_by_id(pokemon_id: int, db: Session = Depends(get_db)):
    start_time = time.time()
    try:
        pokemon = db.query(Pokemon).filter_by(id=pokemon_id).first()
        if not pokemon:
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
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)