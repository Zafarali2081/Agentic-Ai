"""
Service: spark_service.py
Purpose: Distributed Big Data processing using Apache Spark DataFrames and Spark SQL.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

# Adjust import path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.append(str(BACKEND_DIR))

from config import (
    RATINGS_CSV,
    MOVIES_CSV,
    USERS_CSV,
    PYTHON_EXE
)

# PySpark imports
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, IntegerType, FloatType, StringType, LongType
)

_spark_session: Optional[SparkSession] = None


def get_spark_session() -> SparkSession:
    """Returns or initializes the singleton SparkSession configured for local distributed processing."""
    global _spark_session
    if _spark_session is None:
        os.environ["PYSPARK_PYTHON"] = PYTHON_EXE
        os.environ["PYSPARK_DRIVER_PYTHON"] = PYTHON_EXE

        _spark_session = (
            SparkSession.builder
            .appName("CineGraph-SparkEngine")
            .master("local[*]")
            .config("spark.driver.memory", "2g")
            .config("spark.sql.shuffle.partitions", "4")
            .config("spark.ui.enabled", "false")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .config("spark.sql.execution.arrow.pyspark.enabled", "false")
            .getOrCreate()
        )
        _spark_session.sparkContext.setLogLevel("ERROR")
    return _spark_session


class MovieDataProcessor:
    """Encapsulates PySpark DataFrame transformations and Spark SQL operations."""

    def __init__(self, spark: Optional[SparkSession] = None):
        self.spark = spark or get_spark_session()
        self._ratings_df = None
        self._movies_df = None
        self._users_df = None
        self._joined_df = None
        self._load_datasets()

    def _load_datasets(self):
        """Loads processed CSVs into Spark DataFrames with explicit schemas."""
        ratings_schema = StructType([
            StructField("userId", IntegerType(), False),
            StructField("movieId", IntegerType(), False),
            StructField("rating", FloatType(), False),
            StructField("timestamp", LongType(), False),
            StructField("datetime", StringType(), True),
        ])

        movies_schema = StructType([
            StructField("movieId", IntegerType(), False),
            StructField("title", StringType(), False),
            StructField("genres", StringType(), False),
        ])

        users_schema = StructType([
            StructField("userId", IntegerType(), False),
            StructField("age", IntegerType(), True),
            StructField("gender", StringType(), True),
            StructField("occupation", StringType(), True),
            StructField("zip_code", StringType(), True),
        ])

        self._ratings_df = (
            self.spark.read.option("header", "true")
            .schema(ratings_schema)
            .csv(str(RATINGS_CSV))
            .cache()
        )

        self._movies_df = (
            self.spark.read.option("header", "true")
            .schema(movies_schema)
            .csv(str(MOVIES_CSV))
            .cache()
        )

        self._users_df = (
            self.spark.read.option("header", "true")
            .schema(users_schema)
            .csv(str(USERS_CSV))
            .cache()
        )

        # Register Temp SQL Views for Spark SQL queries
        self._ratings_df.createOrReplaceTempView("ratings")
        self._movies_df.createOrReplaceTempView("movies")
        self._users_df.createOrReplaceTempView("users")

        # Joined DataFrame
        self._joined_df = self._ratings_df.join(self._movies_df, on="movieId", how="inner").cache()
        self._joined_df.createOrReplaceTempView("ratings_movies")

    @property
    def ratings_df(self):
        return self._ratings_df

    @property
    def movies_df(self):
        return self._movies_df

    @property
    def users_df(self):
        return self._users_df

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Calculates global dataset metrics using Spark SQL."""
        stats = self.spark.sql("""
            SELECT 
                COUNT(DISTINCT userId) AS total_users,
                COUNT(DISTINCT movieId) AS total_movies,
                COUNT(1) AS total_ratings,
                ROUND(AVG(rating), 2) AS average_rating
            FROM ratings
        """).collect()[0]

        most_popular = self.spark.sql("""
            SELECT m.title, COUNT(r.userId) AS rating_count, ROUND(AVG(r.rating), 2) AS avg_rating
            FROM ratings r
            JOIN movies m ON r.movieId = m.movieId
            GROUP BY m.title
            ORDER BY rating_count DESC
            LIMIT 1
        """).collect()

        pop_title = most_popular[0]["title"] if most_popular else "N/A"
        pop_count = most_popular[0]["rating_count"] if most_popular else 0

        # Unique genres count
        distinct_genres = self.get_distinct_genres()

        return {
            "total_users": int(stats["total_users"]),
            "total_movies": int(stats["total_movies"]),
            "total_ratings": int(stats["total_ratings"]),
            "average_rating": float(stats["average_rating"]),
            "most_popular_movie": pop_title,
            "most_popular_count": int(pop_count),
            "total_genres": len(distinct_genres),
            "genres": distinct_genres
        }

    def get_distinct_genres(self) -> List[str]:
        """Extracts unique genres from the pipe-delimited genre column."""
        exploded = (
            self._movies_df
            .select(F.explode(F.split(F.col("genres"), r"\|")).alias("genre"))
            .filter((F.col("genre") != "") & (F.col("genre") != "Other"))
            .distinct()
            .orderBy("genre")
        )
        return [row["genre"] for row in exploded.collect()]

    def get_popular_movies(self, limit: int = 10, min_ratings: int = 0) -> List[Dict[str, Any]]:
        """Identifies most popular movies sorted by total rating volume."""
        df = (
            self._joined_df
            .groupBy("movieId", "title", "genres")
            .agg(
                F.count("userId").alias("rating_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating")
            )
            .filter(F.col("rating_count") >= min_ratings)
            .orderBy(F.col("rating_count").desc(), F.col("avg_rating").desc())
            .limit(limit)
        )
        return [row.asDict() for row in df.collect()]

    def get_top_rated_movies(self, limit: int = 10, min_ratings: int = 20) -> List[Dict[str, Any]]:
        """Identifies highest rated movies having at least min_ratings votes."""
        df = (
            self._joined_df
            .groupBy("movieId", "title", "genres")
            .agg(
                F.count("userId").alias("rating_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating")
            )
            .filter(F.col("rating_count") >= min_ratings)
            .orderBy(F.col("avg_rating").desc(), F.col("rating_count").desc())
            .limit(limit)
        )
        return [row.asDict() for row in df.collect()]

    def get_rating_distribution(self) -> List[Dict[str, Any]]:
        """Calculates rating frequency breakdown (1.0 to 5.0)."""
        total_ratings = self._ratings_df.count()
        dist = (
            self._ratings_df
            .groupBy("rating")
            .agg(F.count("userId").alias("count"))
            .orderBy("rating")
            .collect()
        )
        return [
            {
                "rating": float(row["rating"]),
                "count": int(row["count"]),
                "percentage": round((row["count"] / total_ratings) * 100, 2)
            }
            for row in dist
        ]

    def get_genre_analytics(self) -> List[Dict[str, Any]]:
        """Analyzes rating counts and average ratings grouped by genre."""
        genre_df = (
            self._joined_df
            .withColumn("genre", F.explode(F.split(F.col("genres"), r"\|")))
            .filter((F.col("genre") != "") & (F.col("genre") != "Other"))
            .groupBy("genre")
            .agg(
                F.count("rating").alias("total_ratings"),
                F.round(F.avg("rating"), 2).alias("avg_rating"),
                F.countDistinct("movieId").alias("movie_count")
            )
            .orderBy(F.col("total_ratings").desc())
        )
        return [row.asDict() for row in genre_df.collect()]

    def get_user_behavior_analytics(self) -> Dict[str, Any]:
        """Analyzes user activity levels, active vs inactive user counts, and distribution."""
        user_agg = (
            self._ratings_df
            .groupBy("userId")
            .agg(
                F.count("rating").alias("user_ratings_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating")
            )
            .withColumn(
                "activity_tier",
                F.when(F.col("user_ratings_count") >= 150, "Power User (>=150)")
                .when(F.col("user_ratings_count") >= 50, "Active (50-149)")
                .otherwise("Casual (<50)")
            )
        )

        tier_summary = (
            user_agg.groupBy("activity_tier")
            .agg(
                F.count("userId").alias("user_count"),
                F.round(F.avg("avg_rating"), 2).alias("tier_avg_rating")
            )
            .collect()
        )

        top_active_users = (
            user_agg.orderBy(F.col("user_ratings_count").desc())
            .limit(10)
            .collect()
        )

        return {
            "tiers": [row.asDict() for row in tier_summary],
            "top_active_users": [row.asDict() for row in top_active_users]
        }

    def get_monthly_activity(self) -> List[Dict[str, Any]]:
        """Calculates monthly rating count and temporal activity trends."""
        monthly = (
            self._ratings_df
            .withColumn("month_year", F.substring(F.col("datetime"), 1, 7))
            .filter(F.col("month_year").isNotNull())
            .groupBy("month_year")
            .agg(
                F.count("rating").alias("rating_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating")
            )
            .orderBy("month_year")
        )
        return [row.asDict() for row in monthly.collect()]

    def search_movies(
        self,
        query: Optional[str] = None,
        genre: Optional[str] = None,
        min_rating: float = 0.0,
        sort_by: str = "rating_count",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Provides filtered, searchable, and paginated movie browsing."""
        # Calculate movie statistics
        stats = (
            self._ratings_df
            .groupBy("movieId")
            .agg(
                F.count("rating").alias("rating_count"),
                F.round(F.avg("rating"), 2).alias("avg_rating")
            )
        )

        df = self._movies_df.join(stats, on="movieId", how="left")
        df = df.fillna({"rating_count": 0, "avg_rating": 0.0})

        if query:
            df = df.filter(F.lower(F.col("title")).contains(query.lower().strip()))

        if genre and genre != "All":
            df = df.filter(F.col("genres").contains(genre))

        if min_rating > 0.0:
            df = df.filter(F.col("avg_rating") >= min_rating)

        total_matches = df.count()

        # Sorting
        if sort_by == "rating_desc":
            df = df.orderBy(F.col("avg_rating").desc(), F.col("rating_count").desc())
        elif sort_by == "title":
            df = df.orderBy(F.col("title").asc())
        elif sort_by == "newest":
            df = df.orderBy(F.col("movieId").desc())
        else: # default rating_count
            df = df.orderBy(F.col("rating_count").desc(), F.col("avg_rating").desc())

        # Pagination
        offset = (page - 1) * page_size
        paged_df = df.limit(offset + page_size).collect()[offset:offset + page_size]

        return {
            "total": total_matches,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_matches + page_size - 1) // page_size if page_size > 0 else 1,
            "movies": [row.asDict() for row in paged_df]
        }
