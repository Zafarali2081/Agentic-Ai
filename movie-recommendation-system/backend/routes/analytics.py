"""
Router: analytics.py
Purpose: Big Data Analytics endpoints for CineGraph dashboard, genres, users, and GraphX graph data.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

from services.data_service import data_service

router = APIRouter(prefix="/api", tags=["Analytics & Big Data"])


@router.get("/dashboard/stats", summary="Get global CineGraph dashboard statistics")
def get_dashboard_stats():
    """Returns high-level platform statistics including rating counts, averages, and distributions."""
    if not data_service.dashboard_stats:
        raise HTTPException(status_code=503, detail="Dataset not initialized. Run preprocessing first.")

    top_popular = data_service.search_movies(sort_by="rating_count", page=1, page_size=10)["movies"]

    return {
        "stats": data_service.dashboard_stats,
        "rating_distribution": data_service.rating_distribution or [],
        "monthly_activity": data_service.monthly_activity or [],
        "top_popular_movies": top_popular
    }


@router.get("/analytics/genres", summary="Get genre breakdown and rating statistics")
def get_genre_analytics():
    """Returns aggregated rating volume, average rating, and movie count across all genres."""
    if not data_service.genre_analytics:
        raise HTTPException(status_code=503, detail="Genre analytics not ready.")
    return {
        "total_genres": len(data_service.genre_analytics),
        "genres": data_service.genre_analytics
    }


@router.get("/analytics/users", summary="Get user activity and behavior segmentation")
def get_user_analytics():
    """Returns user engagement tiers (Casual, Active, Power User) and top active user metrics."""
    if not data_service.user_analytics:
        raise HTTPException(status_code=503, detail="User analytics not ready.")
    return data_service.user_analytics


@router.get("/analytics/graph", summary="Get Scala GraphX bipartite graph analytics results")
def get_graph_analytics():
    """Returns Apache Spark GraphX analytics: Degree centrality, PageRank influence,
    Connected Components, Label Propagation Communities, and representative subgraph for Cytoscape.js."""
    if not data_service.graph_summary:
        raise HTTPException(
            status_code=404,
            detail="GraphX analytics data not found. Please run 'powershell scripts/run_graphx.ps1' to generate it."
        )

    return {
        "summary": data_service.graph_summary,
        "degrees": data_service.degree_distribution or {},
        "pagerank_nodes": data_service.pagerank_nodes or [],
        "communities": data_service.communities or [],
        "subgraph": data_service.graph_sample or {"nodes": [], "edges": []}
    }


@router.get("/analytics/user/{user_id}/preferences", summary="Deep-dive into a specific user's preference profile")
def get_user_preferences(user_id: int):
    """Returns a user's rating distribution, favorite genres, rating history, and activity count."""
    ratings = data_service.get_user_ratings(user_id)
    if not ratings:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found in ratings dataset.")

    genre_prefs = data_service.get_user_genre_preferences(user_id)
    avg_rating = round(sum(r["rating"] for r in ratings) / len(ratings), 2)

    return {
        "userId": user_id,
        "total_ratings": len(ratings),
        "average_rating": avg_rating,
        "favorite_genres": genre_prefs[:5],
        "all_genres": genre_prefs,
        "recent_ratings": ratings[:15]
    }
