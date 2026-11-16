"""
Entrypoint: main.py
Application: CineGraph - Movie Intelligence & Recommendation System API
Technologies: FastAPI, PySpark, Spark MLlib, Spark GraphX, Pandas, Uvicorn
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.append(str(CURRENT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import HOST, PORT, CORS_ORIGINS
from services.data_service import data_service
from routes.analytics import router as analytics_router
from routes.movies import router as movies_router
from routes.recommendations import router as recommendations_router
from routes.models import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes in-memory cache and model instances during server startup."""
    print("==========================================================")
    print("    Starting CineGraph API Server (FastAPI + PySpark)     ")
    print("==========================================================")
    data_service.initialize()
    yield
    print("[*] CineGraph API Server shutdown.")


app = FastAPI(
    title="CineGraph – Movie Intelligence & Recommendation System API",
    description="Big Data Distributed Analytics and Recommendation Engine leveraging Apache Spark, Spark GraphX, and Spark MLlib ALS.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(analytics_router)
app.include_router(movies_router)
app.include_router(recommendations_router)


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint indicating system readiness and model training status."""
    is_trained = data_service.als_recommender.is_trained() if data_service.als_recommender else False
    graph_ready = data_service.graph_summary is not None

    return {
        "status": "healthy",
        "spark_status": "connected",
        "als_model_trained": is_trained,
        "graphx_data_available": graph_ready,
        "version": "1.0.0"
    }


# Mount Frontend Production Build if present
from fastapi.staticfiles import StaticFiles

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    def root():
        return JSONResponse({
            "name": "CineGraph API",
            "documentation": "/docs",
            "health": "/api/health"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
