"""
Pydantic schemas and request/response models for CineGraph API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    spark_status: str
    als_model_trained: bool
    graphx_data_available: bool
    version: str


class PredictRatingRequest(BaseModel):
    user_id: int = Field(..., description="ID of the target user", ge=1)
    movie_id: int = Field(..., description="ID of the movie to evaluate", ge=1)


class PredictRatingResponse(BaseModel):
    userId: int
    movieId: int
    movie_title: Optional[str] = None
    genres: Optional[str] = None
    predicted_rating: float
    is_cold_start: bool
    latency_ms: float


class TrainModelRequest(BaseModel):
    rank: int = Field(default=10, ge=2, le=50, description="Latent factors rank")
    max_iter: int = Field(default=15, ge=1, le=50, description="Max ALS iterations")
    reg_param: float = Field(default=0.1, ge=0.001, le=1.0, description="Regularization parameter")


class MovieItem(BaseModel):
    movieId: int
    title: str
    genres: str
    rating_count: int
    avg_rating: float


class MovieListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    movies: List[MovieItem]


class RecommendationItem(BaseModel):
    movieId: int
    title: str
    genres: str
    predicted_rating: float
    rationale: str
    popularity_score: Optional[float] = None


class RecommendationsResponse(BaseModel):
    userId: int
    algorithm: str
    recommendations: List[RecommendationItem]


class SimilarUserItem(BaseModel):
    userId: int
    similarity_score: float
    similarity_percentage: float


class SimilarUsersResponse(BaseModel):
    userId: int
    similar_users: List[SimilarUserItem]
