"""
Unit and integration tests for CineGraph FastAPI endpoints.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from main import app
from services.data_service import data_service

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_data_service():
    """Ensure data service is initialized before testing."""
    data_service.initialize()


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["als_model_trained"] is True
    assert data["graphx_data_available"] is True


def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert data["stats"]["total_ratings"] == 100000
    assert data["stats"]["total_movies"] == 1682
    assert "rating_distribution" in data


def test_movies_list():
    response = client.get("/api/movies?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1682
    assert len(data["movies"]) == 10


def test_movie_search():
    response = client.get("/api/movies?query=Star%20Wars")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("Star Wars" in m["title"] for m in data["movies"])


def test_graph_analytics():
    response = client.get("/api/analytics/graph")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["total_vertices"] == 2625
    assert len(data["pagerank_nodes"]) > 0


def test_recommendations_als():
    response = client.get("/api/recommendations/1?algorithm=als&k=5")
    assert response.status_code == 200
    data = response.json()
    assert data["userId"] == 1
    assert len(data["recommendations"]) == 5
    assert all("predicted_rating" in r for r in data["recommendations"])


def test_recommendations_popularity():
    response = client.get("/api/recommendations/1?algorithm=popularity&k=5")
    assert response.status_code == 200
    data = response.json()
    assert data["userId"] == 1
    assert len(data["recommendations"]) == 5


def test_predict_rating():
    response = client.post("/api/predict-rating", json={"user_id": 1, "movie_id": 50})
    assert response.status_code == 200
    data = response.json()
    assert data["userId"] == 1
    assert data["movieId"] == 50
    assert 0.5 <= data["predicted_rating"] <= 5.0


def test_similar_users():
    response = client.get("/api/recommendations/1/similar?top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert data["userId"] == 1
    assert len(data["similar_users"]) == 3


def test_model_evaluation():
    response = client.get("/api/model/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "als_metrics" in data
    assert "popularity_baseline_metrics" in data
    assert data["als_metrics"]["rmse"] < data["popularity_baseline_metrics"]["rmse"]
