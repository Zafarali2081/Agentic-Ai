"""
Unit tests for ALS and Popularity recommendation algorithms.
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from recommendation.als_model import ALSRecommender
from recommendation.popularity_model import PopularityRecommender
from services.data_service import data_service


@pytest.fixture(scope="session", autouse=True)
def init_service():
    data_service.initialize()


def test_als_factors_loaded():
    als = ALSRecommender()
    assert als.is_trained() is True
    assert len(als.user_factors) > 0
    assert len(als.item_factors) > 0


def test_als_prediction():
    als = ALSRecommender()
    res = als.predict_rating(user_id=1, movie_id=50)
    assert "predicted_rating" in res
    assert 0.5 <= res["predicted_rating"] <= 5.0
    assert res["is_cold_start"] is False
    assert res["latency_ms"] < 50.0 # Sub-50ms execution latency


def test_als_recommend_top_k():
    als = ALSRecommender()
    recs = als.recommend_for_user(user_id=1, k=10, exclude_rated=True)
    assert len(recs) == 10
    assert all("predicted_rating" in r for r in recs)
    assert all("rationale" in r for r in recs)
    # Check that recommendations are sorted in descending order of predicted rating
    ratings = [r["predicted_rating"] for r in recs]
    assert ratings == sorted(ratings, reverse=True)


def test_als_similar_users():
    als = ALSRecommender()
    sims = als.get_similar_users(user_id=1, top_n=5)
    assert len(sims) == 5
    assert all("similarity_score" in s for s in sims)
    assert all("similarity_percentage" in s for s in sims)
    assert sims[0]["similarity_score"] <= 1.0


def test_popularity_recommender():
    pop = PopularityRecommender()
    pop._ranked_movies = data_service.popularity_recommender._ranked_movies
    recs = pop.recommend_for_user(user_id=1, k=5, exclude_rated=True)
    assert len(recs) == 5
    assert all("popularity_score" in r for r in recs)
