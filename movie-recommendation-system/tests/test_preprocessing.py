"""
Unit tests for data preprocessing and validation pipeline.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(SCRIPTS_DIR))

from preprocess_data import clean_and_validate, train_test_split
from config import RATINGS_CSV, MOVIES_CSV, USERS_CSV


def test_processed_files_exist():
    assert RATINGS_CSV.exists()
    assert MOVIES_CSV.exists()
    assert USERS_CSV.exists()


def test_ratings_schema_and_boundaries():
    df = pd.read_csv(RATINGS_CSV)
    assert "userId" in df.columns
    assert "movieId" in df.columns
    assert "rating" in df.columns
    assert "timestamp" in df.columns

    # Verify no invalid ratings
    assert df["rating"].min() >= 0.5
    assert df["rating"].max() <= 5.0
    assert len(df) == 100000


def test_movies_schema_and_genres():
    df = pd.read_csv(MOVIES_CSV)
    assert "movieId" in df.columns
    assert "title" in df.columns
    assert "genres" in df.columns
    assert len(df) == 1682
    # Ensure genres are pipe-separated or non-empty
    assert not df["genres"].isna().any()


def test_clean_and_validate_logic():
    dummy_ratings = pd.DataFrame({
        "userId": [1, 1, 2, np.nan],
        "movieId": [10, 10, 20, 30],
        "rating": [4.0, 5.0, 99.0, 3.0], # 99.0 is invalid
        "timestamp": [100, 200, 300, 400]
    })
    dummy_movies = pd.DataFrame({
        "movieId": [10, 20],
        "title": ["Movie A", "Movie B"],
        "genres": ["Action", "Drama"]
    })
    dummy_users = pd.DataFrame({"userId": [1, 2]})

    clean_r, clean_m, clean_u = clean_and_validate(dummy_ratings, dummy_movies, dummy_users)

    # User 1 has two ratings for movie 10; keep="last" keeps the latest timestamp (5.0)
    assert len(clean_r) == 1
    assert clean_r.iloc[0]["rating"] == 5.0
    assert clean_r.iloc[0]["movieId"] == 10


def test_train_test_split_ratio():
    df = pd.read_csv(RATINGS_CSV)
    train_df, test_df = train_test_split(df.head(1000), test_ratio=0.20, seed=42)

    total = len(train_df) + len(test_df)
    assert total == 1000
    assert 0.15 <= len(test_df) / total <= 0.25
