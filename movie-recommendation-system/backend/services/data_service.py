"""
Service: data_service.py
Purpose: High-performance in-memory cache manager for movie metadata, GraphX analytics,
ALS models, and baseline recommendation algorithms.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.append(str(BACKEND_DIR))

from config import (
    RATINGS_CSV,
    MOVIES_CSV,
    USERS_CSV,
    TRAIN_RATINGS_CSV,
    TEST_RATINGS_CSV,
    GRAPH_SUMMARY_JSON,
    DEGREE_DIST_JSON,
    PAGERANK_NODES_JSON,
    COMMUNITIES_JSON,
    GRAPH_EDGES_SAMPLE_JSON,
    EVALUATION_METRICS_PATH,
)

from recommendation.als_model import ALSRecommender
from recommendation.popularity_model import PopularityRecommender


class CineGraphDataService:
    """Singleton service providing in-memory caching and rapid query serving."""

    def __init__(self):
        self.movies_df: Optional[pd.DataFrame] = None
        self.ratings_df: Optional[pd.DataFrame] = None
        self.users_df: Optional[pd.DataFrame] = None
        self.movie_dict: Dict[int, Dict[str, Any]] = {}
        self.als_recommender: Optional[ALSRecommender] = None
        self.popularity_recommender: Optional[PopularityRecommender] = None
        self.dashboard_stats: Optional[Dict[str, Any]] = None
        self.genre_analytics: Optional[List[Dict[str, Any]]] = None
        self.user_analytics: Optional[Dict[str, Any]] = None
        self.rating_distribution: Optional[List[Dict[str, Any]]] = None
        self.monthly_activity: Optional[List[Dict[str, Any]]] = None
        self.graph_summary: Optional[Dict[str, Any]] = None
        self.degree_distribution: Optional[Dict[str, Any]] = None
        self.pagerank_nodes: Optional[List[Dict[str, Any]]] = None
        self.communities: Optional[List[Dict[str, Any]]] = None
        self.graph_sample: Optional[Dict[str, Any]] = None
        self.evaluation_metrics: Optional[Dict[str, Any]] = None

    def initialize(self):
        """Pre-loads CSVs, GraphX outputs, and model instances."""
        print("[*] Initializing CineGraph Data Service in-memory cache...")

        # 1. Load CSVs
        if MOVIES_CSV.exists() and RATINGS_CSV.exists():
            self.movies_df = pd.read_csv(MOVIES_CSV)
            self.ratings_df = pd.read_csv(RATINGS_CSV)
            if USERS_CSV.exists():
                self.users_df = pd.read_csv(USERS_CSV)

            # Pre-compute movie statistics for rapid exploration
            m_stats = (
                self.ratings_df.groupby("movieId")
                .agg(
                    rating_count=("rating", "count"),
                    avg_rating=("rating", "mean")
                )
                .reset_index()
            )
            m_stats["avg_rating"] = m_stats["avg_rating"].round(2)

            merged = pd.merge(self.movies_df, m_stats, on="movieId", how="left")
            merged["rating_count"] = merged["rating_count"].fillna(0).astype(int)
            merged["avg_rating"] = merged["avg_rating"].fillna(0.0).astype(float)

            self.movies_df = merged

            for _, row in self.movies_df.iterrows():
                mid = int(row["movieId"])
                self.movie_dict[mid] = {
                    "movieId": mid,
                    "title": str(row["title"]),
                    "genres": str(row["genres"]),
                    "rating_count": int(row["rating_count"]),
                    "avg_rating": float(row["avg_rating"]),
                }

            # 2. Pre-compute Dashboard Statistics
            total_users = int(self.ratings_df["userId"].nunique())
            total_movies = int(self.movies_df["movieId"].nunique())
            total_ratings = int(len(self.ratings_df))
            avg_rating = round(float(self.ratings_df["rating"].mean()), 2)

            most_pop = self.movies_df.sort_values("rating_count", ascending=False).iloc[0]

            # Genres
            all_genres = set()
            for g_str in self.movies_df["genres"].dropna():
                for g in str(g_str).split("|"):
                    if g and g != "Other":
                        all_genres.add(g)

            self.dashboard_stats = {
                "total_users": total_users,
                "total_movies": total_movies,
                "total_ratings": total_ratings,
                "average_rating": avg_rating,
                "most_popular_movie": str(most_pop["title"]),
                "most_popular_count": int(most_pop["rating_count"]),
                "total_genres": len(all_genres),
                "genres": sorted(list(all_genres))
            }

            # 3. Rating Distribution
            counts = self.ratings_df["rating"].value_counts().sort_index()
            self.rating_distribution = [
                {
                    "rating": float(r),
                    "count": int(c),
                    "percentage": round((c / total_ratings) * 100, 2)
                }
                for r, c in counts.items()
            ]

            # 4. Genre Breakdown
            genre_rows = []
            for _, r in self.ratings_df.iterrows():
                mid = int(r["movieId"])
                rating = float(r["rating"])
                m_info = self.movie_dict.get(mid)
                if m_info:
                    for g in m_info["genres"].split("|"):
                        if g and g != "Other":
                            genre_rows.append({"genre": g, "rating": rating, "movieId": mid})

            gdf = pd.DataFrame(genre_rows)
            g_agg = (
                gdf.groupby("genre")
                .agg(
                    total_ratings=("rating", "count"),
                    avg_rating=("rating", "mean"),
                    movie_count=("movieId", "nunique")
                )
                .reset_index()
                .sort_values("total_ratings", ascending=False)
            )
            g_agg["avg_rating"] = g_agg["avg_rating"].round(2)
            self.genre_analytics = g_agg.to_dict(orient="records")

            # 5. Monthly Activity
            if "datetime" in self.ratings_df.columns:
                self.ratings_df["month_year"] = self.ratings_df["datetime"].str[:7]
                m_act = (
                    self.ratings_df.groupby("month_year")
                    .agg(
                        rating_count=("rating", "count"),
                        avg_rating=("rating", "mean")
                    )
                    .reset_index()
                    .sort_values("month_year")
                )
                m_act["avg_rating"] = m_act["avg_rating"].round(2)
                self.monthly_activity = m_act.to_dict(orient="records")

            # 6. User Behavior
            u_agg = (
                self.ratings_df.groupby("userId")
                .agg(
                    user_ratings_count=("rating", "count"),
                    avg_rating=("rating", "mean")
                )
                .reset_index()
            )
            u_agg["avg_rating"] = u_agg["avg_rating"].round(2)

            def get_tier(cnt):
                if cnt >= 150:
                    return "Power User (>=150)"
                elif cnt >= 50:
                    return "Active (50-149)"
                else:
                    return "Casual (<50)"

            u_agg["activity_tier"] = u_agg["user_ratings_count"].apply(get_tier)
            tier_summary = (
                u_agg.groupby("activity_tier")
                .agg(
                    user_count=("userId", "count"),
                    tier_avg_rating=("avg_rating", "mean")
                )
                .reset_index()
            )
            tier_summary["tier_avg_rating"] = tier_summary["tier_avg_rating"].round(2)

            top_users = (
                u_agg.sort_values("user_ratings_count", ascending=False)
                .head(10)
                .to_dict(orient="records")
            )

            self.user_analytics = {
                "tiers": tier_summary.to_dict(orient="records"),
                "top_active_users": top_users
            }

        # 7. Load GraphX Output JSONs
        self.load_graph_data()

        # 8. Load Models
        self.als_recommender = ALSRecommender()
        self.popularity_recommender = PopularityRecommender()
        self._init_popularity_baseline()

        # 9. Load Evaluation Metrics
        self.load_evaluation_metrics()

        print("[OK] CineGraph Data Service initialization complete.")

    def load_graph_data(self):
        """Loads GraphX analysis results from data/graph/."""
        if GRAPH_SUMMARY_JSON.exists():
            with open(GRAPH_SUMMARY_JSON, "r") as f:
                self.graph_summary = json.load(f)
        if DEGREE_DIST_JSON.exists():
            with open(DEGREE_DIST_JSON, "r") as f:
                self.degree_distribution = json.load(f)
        if PAGERANK_NODES_JSON.exists():
            with open(PAGERANK_NODES_JSON, "r") as f:
                self.pagerank_nodes = json.load(f)
        if COMMUNITIES_JSON.exists():
            with open(COMMUNITIES_JSON, "r") as f:
                self.communities = json.load(f)
        if GRAPH_EDGES_SAMPLE_JSON.exists():
            with open(GRAPH_EDGES_SAMPLE_JSON, "r") as f:
                self.graph_sample = json.load(f)

    def load_evaluation_metrics(self):
        """Loads evaluation metrics from models/evaluation_metrics.json."""
        if EVALUATION_METRICS_PATH.exists():
            with open(EVALUATION_METRICS_PATH, "r") as f:
                self.evaluation_metrics = json.load(f)

    def _init_popularity_baseline(self):
        """Initializes popularity-weighted baseline from in-memory movie statistics."""
        if self.movies_df is not None:
            m = 20.0
            C = self.dashboard_stats.get("average_rating", 3.53) if self.dashboard_stats else 3.53

            ranked = []
            for mid, info in self.movie_dict.items():
                v = float(info["rating_count"])
                R = float(info["avg_rating"])
                weighted_score = ((v / (v + m)) * R) + ((m / (v + m)) * C)
                ranked.append({
                    "movieId": mid,
                    "title": info["title"],
                    "genres": info["genres"],
                    "rating_count": int(v),
                    "avg_rating": round(R, 2),
                    "weighted_score": round(weighted_score, 2),
                    "R": R
                })

            ranked.sort(key=lambda x: x["weighted_score"], reverse=True)
            self.popularity_recommender._ranked_movies = ranked

    def search_movies(
        self,
        query: Optional[str] = None,
        genre: Optional[str] = None,
        min_rating: float = 0.0,
        sort_by: str = "rating_count",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Provides filtered, searchable, and paginated movie browsing directly from memory."""
        if self.movies_df is None:
            return {"total": 0, "page": page, "page_size": page_size, "total_pages": 0, "movies": []}

        df = self.movies_df

        if query:
            df = df[df["title"].str.lower().str.contains(query.lower().strip(), na=False)]

        if genre and genre != "All":
            df = df[df["genres"].str.contains(genre, na=False)]

        if min_rating > 0.0:
            df = df[df["avg_rating"] >= min_rating]

        total_matches = len(df)

        if sort_by == "rating_desc":
            df = df.sort_values(by=["avg_rating", "rating_count"], ascending=[False, False])
        elif sort_by == "title":
            df = df.sort_values(by="title", ascending=True)
        elif sort_by == "newest":
            df = df.sort_values(by="movieId", ascending=False)
        else:
            df = df.sort_values(by=["rating_count", "avg_rating"], ascending=[False, False])

        offset = (page - 1) * page_size
        paged = df.iloc[offset:offset + page_size].to_dict(orient="records")

        return {
            "total": total_matches,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_matches + page_size - 1) // page_size if page_size > 0 else 1,
            "movies": paged
        }

    def get_user_ratings(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves history of movies rated by the user."""
        if self.ratings_df is None:
            return []
        u_ratings = self.ratings_df[self.ratings_df["userId"] == user_id]
        results = []
        for _, row in u_ratings.iterrows():
            mid = int(row["movieId"])
            m_info = self.movie_dict.get(mid, {"title": f"Movie {mid}", "genres": "General"})
            results.append({
                "movieId": mid,
                "title": m_info["title"],
                "genres": m_info["genres"],
                "rating": float(row["rating"]),
                "datetime": str(row.get("datetime", ""))
            })
        results.sort(key=lambda x: x["rating"], reverse=True)
        return results

    def get_user_genre_preferences(self, user_id: int) -> List[Dict[str, Any]]:
        """Computes genre breakdown and preference weights for a specific user."""
        history = self.get_user_ratings(user_id)
        if not history:
            return []

        genre_counts = {}
        genre_ratings = {}

        for item in history:
            r = item["rating"]
            for g in item["genres"].split("|"):
                if g and g != "Other":
                    genre_counts[g] = genre_counts.get(g, 0) + 1
                    genre_ratings.setdefault(g, []).append(r)

        results = [
            {
                "genre": g,
                "count": genre_counts[g],
                "avg_rating": round(sum(genre_ratings[g]) / len(genre_ratings[g]), 2)
            }
            for g in genre_counts
        ]
        results.sort(key=lambda x: (x["count"], x["avg_rating"]), reverse=True)
        return results


# Global singleton
data_service = CineGraphDataService()
