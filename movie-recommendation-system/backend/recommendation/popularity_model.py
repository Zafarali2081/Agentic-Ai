"""
Module: popularity_model.py
Purpose: Baseline Popularity-Based Recommendation Engine using Bayesian-Weighted Ranking.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from pyspark.sql import functions as F


class PopularityRecommender:
    """Baseline recommender utilizing Bayesian-weighted movie popularity scores."""

    def __init__(self, processor=None, min_votes_threshold: int = 20):
        self.min_votes = min_votes_threshold
        self.processor = processor
        self.global_mean: float = 3.53
        self._ranked_movies: Optional[List[Dict[str, Any]]] = None

    def fit(self, processor):
        """Computes Bayesian-weighted popularity score for every movie."""
        self.processor = processor

        # Global average rating
        mean_row = processor.ratings_df.select(F.avg("rating").alias("mean_r")).collect()
        if mean_row and mean_row[0]["mean_r"] is not None:
            self.global_mean = float(mean_row[0]["mean_r"])

        # Movie stats
        m = float(self.min_votes)
        C = self.global_mean

        stats = (
            processor.ratings_df
            .groupBy("movieId")
            .agg(
                F.count("rating").alias("v"),
                F.avg("rating").alias("R")
            )
            .withColumn(
                "weighted_score",
                ((F.col("v") / (F.col("v") + m)) * F.col("R")) +
                ((m / (F.col("v") + m)) * C)
            )
        )

        ranked_df = (
            processor.movies_df
            .join(stats, on="movieId", how="inner")
            .orderBy(F.col("weighted_score").desc())
        )

        self._ranked_movies = [row.asDict() for row in ranked_df.collect()]
        print(f"[OK] Popularity Recommender fitted on {len(self._ranked_movies)} movies.")

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """Predicts rating as the historical average rating of the movie (or global mean)."""
        if self._ranked_movies:
            for m in self._ranked_movies:
                if m["movieId"] == movie_id:
                    return round(float(m.get("R", self.global_mean)), 2)
        return round(self.global_mean, 2)

    def recommend_for_user(
        self,
        user_id: int,
        k: int = 10,
        exclude_rated: bool = True
    ) -> List[Dict[str, Any]]:
        """Recommends Top-K most popular weighted movies not yet seen by the user."""
        if not self._ranked_movies:
            if self.processor:
                self.fit(self.processor)
            else:
                return []

        rated_movie_ids = set()
        if exclude_rated and self.processor:
            user_ratings = (
                self.processor.ratings_df
                .filter(F.col("userId") == user_id)
                .select("movieId")
                .collect()
            )
            rated_movie_ids = {r["movieId"] for r in user_ratings}

        recommendations = []
        for m in self._ranked_movies:
            if m["movieId"] not in rated_movie_ids:
                recommendations.append({
                    "movieId": m["movieId"],
                    "title": m["title"],
                    "genres": m["genres"],
                    "predicted_rating": round(float(m.get("R", self.global_mean)), 2),
                    "popularity_score": round(float(m["weighted_score"]), 2),
                    "rationale": "High global viewer popularity and high weighted consensus score."
                })
                if len(recommendations) >= k:
                    break

        return recommendations
