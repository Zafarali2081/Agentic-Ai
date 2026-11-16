"""
Script: preprocess_data.py
Purpose: Cleans, validates, transforms, and splits the MovieLens dataset into standard CSV files.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# Adjust path to import config
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT / "backend"))

sys.stdout.reconfigure(encoding="utf-8")

from config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    RATINGS_CSV,
    MOVIES_CSV,
    USERS_CSV,
    TRAIN_RATINGS_CSV,
    TEST_RATINGS_CSV,
)

GENRE_NAMES_100K = [
    "unknown", "Action", "Adventure", "Animation", "Children's", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror",
    "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
]


def load_raw_ml100k(raw_dir: Path):
    """Loads raw ML-100K files from u.data, u.item, and u.user."""
    data_file = raw_dir / "ml-100k" / "u.data"
    item_file = raw_dir / "ml-100k" / "u.item"
    user_file = raw_dir / "ml-100k" / "u.user"

    if not data_file.exists():
        raise FileNotFoundError(f"Missing {data_file}. Please run download_dataset.py first.")

    # 1. Ratings
    ratings_df = pd.read_csv(
        data_file,
        sep="\t",
        names=["userId", "movieId", "rating", "timestamp"],
        engine="python"
    )

    # 2. Movies
    movie_cols = [
        "movieId", "title", "release_date", "video_release_date", "IMDb_URL"
    ] + GENRE_NAMES_100K

    movies_raw = pd.read_csv(
        item_file,
        sep="|",
        names=movie_cols,
        encoding="latin-1",
        engine="python"
    )

    # Convert binary genre columns to pipe-separated genre string
    def extract_genres(row):
        active = [g for g in GENRE_NAMES_100K if g != "unknown" and row[g] == 1]
        return "|".join(active) if active else "Other"

    movies_raw["genres"] = movies_raw.apply(extract_genres, axis=1)
    movies_df = movies_raw[["movieId", "title", "genres"]].copy()

    # 3. Users
    if user_file.exists():
        users_df = pd.read_csv(
            user_file,
            sep="|",
            names=["userId", "age", "gender", "occupation", "zip_code"],
            encoding="latin-1",
            engine="python"
        )
    else:
        unique_users = ratings_df["userId"].unique()
        users_df = pd.DataFrame({
            "userId": unique_users,
            "age": 25,
            "gender": "M",
            "occupation": "other",
            "zip_code": "00000"
        })

    return ratings_df, movies_df, users_df


def load_raw_ml_latest_small(raw_dir: Path):
    """Fallback for ml-latest-small directory."""
    folder = raw_dir / "ml-latest-small"
    ratings_df = pd.read_csv(folder / "ratings.csv")
    movies_df = pd.read_csv(folder / "movies.csv")

    unique_users = ratings_df["userId"].unique()
    users_df = pd.DataFrame({
        "userId": unique_users,
        "age": 25,
        "gender": "M",
        "occupation": "other",
        "zip_code": "00000"
    })
    return ratings_df, movies_df, users_df


def clean_and_validate(ratings_df: pd.DataFrame, movies_df: pd.DataFrame, users_df: pd.DataFrame):
    """Applies deduplication, validation, type conversions, and formatting."""
    print("[*] Performing data cleaning and validation...")

    # 1. Clean Ratings
    ratings_df = ratings_df.dropna(subset=["userId", "movieId", "rating"]).copy()
    ratings_df["userId"] = ratings_df["userId"].astype(int)
    ratings_df["movieId"] = ratings_df["movieId"].astype(int)
    ratings_df["rating"] = ratings_df["rating"].astype(float)
    ratings_df["timestamp"] = ratings_df["timestamp"].astype(int)

    # Validate rating scale
    ratings_df = ratings_df[(ratings_df["rating"] >= 0.5) & (ratings_df["rating"] <= 5.0)]

    # Deduplicate: keep the latest rating for any user-movie pair
    ratings_df = ratings_df.sort_values("timestamp").drop_duplicates(
        subset=["userId", "movieId"], keep="last"
    )

    # Human-readable UTC timestamp
    ratings_df["datetime"] = ratings_df["timestamp"].apply(
        lambda ts: datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    )

    # 2. Clean Movies
    movies_df = movies_df.dropna(subset=["movieId", "title"]).copy()
    movies_df["movieId"] = movies_df["movieId"].astype(int)
    movies_df["title"] = movies_df["title"].astype(str).str.strip()
    movies_df["genres"] = movies_df["genres"].fillna("Other").astype(str).str.strip()
    movies_df = movies_df.drop_duplicates(subset=["movieId"])

    # 3. Clean Users
    users_df = users_df.dropna(subset=["userId"]).copy()
    users_df["userId"] = users_df["userId"].astype(int)
    users_df = users_df.drop_duplicates(subset=["userId"])

    # Ensure referential integrity: only keep ratings for movies that exist
    valid_movie_ids = set(movies_df["movieId"])
    ratings_df = ratings_df[ratings_df["movieId"].isin(valid_movie_ids)]

    print(f"[+] Cleaned Records: Ratings={len(ratings_df)}, Movies={len(movies_df)}, Users={len(users_df)}")
    return ratings_df, movies_df, users_df


def train_test_split(ratings_df: pd.DataFrame, test_ratio: float = 0.20, seed: int = 42):
    """Splits ratings into train and test sets deterministically per user."""
    print(f"[*] Splitting dataset into train ({int((1-test_ratio)*100)}%) and test ({int(test_ratio*100)}%)...")
    np.random.seed(seed)

    # Stratified per user to ensure every user has test coverage
    train_indices = []
    test_indices = []

    for user_id, group in ratings_df.groupby("userId"):
        indices = group.index.values
        n_items = len(indices)
        if n_items < 5:
            # Not enough reviews to safely split; assign all to train
            train_indices.extend(indices)
        else:
            n_test = max(1, int(n_items * test_ratio))
            shuffled = np.random.permutation(indices)
            test_indices.extend(shuffled[:n_test])
            train_indices.extend(shuffled[n_test:])

    train_df = ratings_df.loc[train_indices].sort_values(["userId", "movieId"])
    test_df = ratings_df.loc[test_indices].sort_values(["userId", "movieId"])

    print(f"[+] Train ratings: {len(train_df)}, Test ratings: {len(test_df)}")
    return train_df, test_df


def save_processed_datasets(ratings_df, movies_df, users_df, train_df, test_df):
    """Saves processed CSV files to data/processed."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    ratings_df.to_csv(RATINGS_CSV, index=False)
    movies_df.to_csv(MOVIES_CSV, index=False)
    users_df.to_csv(USERS_CSV, index=False)
    train_df.to_csv(TRAIN_RATINGS_CSV, index=False)
    test_df.to_csv(TEST_RATINGS_CSV, index=False)

    print(f"[OK] Processed files saved successfully to {PROCESSED_DATA_DIR}:")
    print(f"    - {RATINGS_CSV.name} ({len(ratings_df)} rows)")
    print(f"    - {MOVIES_CSV.name} ({len(movies_df)} rows)")
    print(f"    - {USERS_CSV.name} ({len(users_df)} rows)")
    print(f"    - {TRAIN_RATINGS_CSV.name} ({len(train_df)} rows)")
    print(f"    - {TEST_RATINGS_CSV.name} ({len(test_df)} rows)")


def main():
    if (RAW_DATA_DIR / "ml-100k" / "u.data").exists():
        ratings, movies, users = load_raw_ml100k(RAW_DATA_DIR)
    elif (RAW_DATA_DIR / "ml-latest-small" / "ratings.csv").exists():
        ratings, movies, users = load_raw_ml_latest_small(RAW_DATA_DIR)
    else:
        print("[!] Raw dataset not found. Running download_dataset.py...")
        from download_dataset import main as download_main
        download_main()
        if (RAW_DATA_DIR / "ml-100k" / "u.data").exists():
            ratings, movies, users = load_raw_ml100k(RAW_DATA_DIR)
        else:
            ratings, movies, users = load_raw_ml_latest_small(RAW_DATA_DIR)

    cleaned_ratings, cleaned_movies, cleaned_users = clean_and_validate(ratings, movies, users)
    train_ratings, test_ratings = train_test_split(cleaned_ratings, test_ratio=0.20, seed=42)
    save_processed_datasets(cleaned_ratings, cleaned_movies, cleaned_users, train_ratings, test_ratings)


if __name__ == "__main__":
    main()
