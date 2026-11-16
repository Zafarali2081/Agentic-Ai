"""
Router: recommendations.py
Purpose: Recommendation endpoints for ALS Collaborative Filtering, Popularity baseline,
rating prediction, user similarity, and model evaluation metrics.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
import time

from services.data_service import data_service
from routes.models import (
    PredictRatingRequest,
    PredictRatingResponse,
    TrainModelRequest,
    RecommendationsResponse,
    SimilarUsersResponse
)

router = APIRouter(prefix="/api", tags=["Recommendations & ML Models"])


@router.get("/recommendations/{user_id}", response_model=RecommendationsResponse, summary="Get personalized movie recommendations")
def get_user_recommendations(
    user_id: int,
    algorithm: str = Query("als", description="Recommendation algorithm: 'als' (Collaborative Filtering) or 'popularity' (Baseline)"),
    k: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    exclude_rated: bool = Query(True, description="Exclude movies already rated by the user")
):
    """Generates personalized Top-K movie recommendations using either Spark MLlib ALS or Popularity Baseline."""
    if algorithm.lower() == "popularity":
        if not data_service.popularity_recommender:
            raise HTTPException(status_code=503, detail="Popularity recommender is not ready.")
        recs = data_service.popularity_recommender.recommend_for_user(
            user_id=user_id, k=k, exclude_rated=exclude_rated
        )
        return {
            "userId": user_id,
            "algorithm": "Bayesian-Weighted Popularity Baseline",
            "recommendations": recs
        }

    # Default to ALS Recommender
    if not data_service.als_recommender or not data_service.als_recommender.is_trained():
        raise HTTPException(
            status_code=400,
            detail="ALS Collaborative Filtering model is not trained yet. Use POST /api/model/train or run scripts/train_model.py."
        )

    try:
        recs = data_service.als_recommender.recommend_for_user(
            user_id=user_id, k=k, exclude_rated=exclude_rated
        )
        return {
            "userId": user_id,
            "algorithm": "Apache Spark MLlib ALS (Collaborative Filtering)",
            "recommendations": recs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/recommendations/{user_id}/similar", response_model=SimilarUsersResponse, summary="Find similar users by taste profile")
def get_similar_users(
    user_id: int,
    top_n: int = Query(5, ge=1, le=20, description="Number of similar users to find")
):
    """Finds peer users with matching taste vectors calculated via Cosine Similarity over ALS latent factors."""
    if not data_service.als_recommender or not data_service.als_recommender.is_trained():
        raise HTTPException(status_code=400, detail="ALS model must be trained to compute user similarity vectors.")

    sims = data_service.als_recommender.get_similar_users(user_id=user_id, top_n=top_n)
    if not sims:
        raise HTTPException(status_code=404, detail=f"No similar users found or User {user_id} has insufficient ratings.")

    return {
        "userId": user_id,
        "similar_users": sims
    }


@router.post("/predict-rating", response_model=PredictRatingResponse, summary="Predict user rating for a specific movie")
def predict_rating(request: PredictRatingRequest):
    """Calculates predicted rating (1.0 - 5.0) for a given user and movie pair using MLlib latent factor product."""
    if not data_service.als_recommender or not data_service.als_recommender.is_trained():
        raise HTTPException(status_code=400, detail="ALS model is not trained. Please train the model first.")

    res = data_service.als_recommender.predict_rating(user_id=request.user_id, movie_id=request.movie_id)
    movie = data_service.movie_dict.get(request.movie_id)

    return {
        "userId": request.user_id,
        "movieId": request.movie_id,
        "movie_title": movie["title"] if movie else f"Movie {request.movie_id}",
        "genres": movie["genres"] if movie else "Unknown",
        "predicted_rating": res["predicted_rating"],
        "is_cold_start": res["is_cold_start"],
        "latency_ms": res["latency_ms"]
    }


@router.get("/model/evaluation", summary="Get model evaluation metrics and comparison matrix")
def get_model_evaluation():
    """Returns evaluation results: RMSE, MAE, Precision@K, Recall@K, training time,
    prediction latency, and ALS vs Popularity baseline comparison."""
    if not data_service.evaluation_metrics:
        raise HTTPException(
            status_code=404,
            detail="Evaluation metrics not found. Train the model using POST /api/model/train or run scripts/train_model.py."
        )
    return data_service.evaluation_metrics


def _train_in_background(rank: int, max_iter: int, reg_param: float):
    """Executes distributed training using Spark MLlib and refreshes the cache."""
    print(f"[*] Starting background ALS model retraining (rank={rank}, max_iter={max_iter}, reg_param={reg_param})...")
    from config import TRAIN_RATINGS_CSV
    from services.spark_service import get_spark_session, MovieDataProcessor
    from recommendation.evaluation import ModelEvaluator
    from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, LongType

    spark = get_spark_session()
    processor = MovieDataProcessor(spark)

    train_schema = StructType([
        StructField("userId", IntegerType(), False),
        StructField("movieId", IntegerType(), False),
        StructField("rating", FloatType(), False),
        StructField("timestamp", LongType(), False),
    ])

    train_df = (
        spark.read.option("header", "true")
        .schema(train_schema)
        .csv(str(TRAIN_RATINGS_CSV))
        .cache()
    )

    data_service.als_recommender.train(train_df, rank=rank, max_iter=max_iter, reg_param=reg_param)
    data_service.popularity_recommender.fit(processor)

    evaluator = ModelEvaluator(spark)
    results = evaluator.evaluate(data_service.als_recommender, data_service.popularity_recommender, processor)
    data_service.evaluation_metrics = results
    print("[OK] Background model retraining and evaluation complete.")


@router.post("/model/train", summary="Trigger ALS Collaborative Filtering model retraining")
def train_model(request: TrainModelRequest, background_tasks: BackgroundTasks):
    """Initiates an asynchronous Spark MLlib ALS model training run with custom hyperparameters."""
    background_tasks.add_task(_train_in_background, request.rank, request.max_iter, request.reg_param)
    return {
        "status": "training_initiated",
        "message": f"Spark MLlib ALS training initiated in background with rank={request.rank}, maxIter={request.max_iter}, regParam={request.reg_param}."
    }
