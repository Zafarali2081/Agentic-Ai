"""
Router: movies.py
Purpose: Movie catalog endpoints for browsing, searching, and filtering movies.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

from services.data_service import data_service
from routes.models import MovieListResponse

router = APIRouter(prefix="/api/movies", tags=["Movie Catalog"])


@router.get("", response_model=MovieListResponse, summary="Search and filter movies with pagination")
def list_movies(
    query: Optional[str] = Query(None, description="Search keyword in movie title"),
    genre: Optional[str] = Query(None, description="Filter by genre (e.g. Action, Drama, Sci-Fi)"),
    min_rating: float = Query(0.0, ge=0.0, le=5.0, description="Minimum average rating threshold"),
    sort_by: str = Query("rating_count", description="Sort by: rating_count, rating_desc, title, newest"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Retrieves paginated movies with optional title search, genre filters, and rating boundaries."""
    return data_service.search_movies(
        query=query,
        genre=genre,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )


@router.get("/popular", summary="Get most popular movies by total rating volume")
def get_popular_movies(limit: int = Query(10, ge=1, le=50)):
    """Returns top movies with highest rating volume."""
    res = data_service.search_movies(sort_by="rating_count", page=1, page_size=limit)
    return res["movies"]


@router.get("/top-rated", summary="Get highest rated movies (minimum 20 ratings)")
def get_top_rated_movies(
    limit: int = Query(10, ge=1, le=50),
    min_ratings: int = Query(20, ge=1, description="Minimum ratings threshold to prevent outliers")
):
    """Returns top rated movies having at least min_ratings reviews."""
    if data_service.movies_df is None:
        raise HTTPException(status_code=503, detail="Movie catalog not loaded.")

    filtered = data_service.movies_df[data_service.movies_df["rating_count"] >= min_ratings]
    sorted_df = filtered.sort_values(by=["avg_rating", "rating_count"], ascending=[False, False])
    return sorted_df.head(limit).to_dict(orient="records")


@router.get("/{movie_id}", summary="Get movie details by ID")
def get_movie_by_id(movie_id: int):
    """Returns specific movie metadata and rating count."""
    movie = data_service.movie_dict.get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} was not found.")
    return movie
