"""
Script: train_model.py
Purpose: Trains the Spark MLlib ALS collaborative filtering model and computes evaluation metrics.
"""

import sys
import os
from pathlib import Path

# Fix python path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.append(str(BACKEND_DIR))

# Ensure utf-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

from config import TRAIN_RATINGS_CSV
from services.spark_service import get_spark_session, MovieDataProcessor
from recommendation.als_model import ALSRecommender
from recommendation.popularity_model import PopularityRecommender
from recommendation.evaluation import ModelEvaluator

from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, LongType


def main():
    print("==========================================================")
    print("    CineGraph: Spark MLlib Model Training & Evaluation    ")
    print("==========================================================")

    spark = get_spark_session()
    processor = MovieDataProcessor(spark)

    print(f"[*] Loading training ratings from {TRAIN_RATINGS_CSV}...")
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

    print(f"[+] Loaded {train_df.count()} training ratings.")

    # 1. Train ALS Recommender
    print("[*] Training Spark MLlib ALS model (rank=10, maxIter=15, regParam=0.1)...")
    als = ALSRecommender()
    train_time = als.train(train_df, rank=10, max_iter=15, reg_param=0.1)
    print(f"[OK] ALS Model successfully trained in {train_time} seconds.")

    # 2. Fit Popularity Recommender
    print("[*] Fitting Baseline Popularity model...")
    pop_model = PopularityRecommender()
    pop_model.fit(processor)

    # 3. Comprehensive Evaluation
    evaluator = ModelEvaluator(spark)
    results = evaluator.evaluate(als, pop_model, processor)

    print("\n==========================================================")
    print("              MODEL EVALUATION RESULTS                    ")
    print("==========================================================")
    print(f"Algorithm:       {results['model_metadata']['algorithm']}")
    print(f"ALS RMSE:        {results['als_metrics']['rmse']}")
    print(f"Baseline RMSE:   {results['popularity_baseline_metrics']['rmse']}")
    print(f"ALS MAE:         {results['als_metrics']['mae']}")
    print(f"Baseline MAE:    {results['popularity_baseline_metrics']['mae']}")
    print(f"ALS P@10:        {results['als_metrics']['precision_at_10']}")
    print(f"Baseline P@10:   {results['popularity_baseline_metrics']['precision_at_10']}")
    print(f"ALS Recall@10:   {results['als_metrics']['recall_at_10']}")
    print(f"Training Time:   {results['als_metrics']['training_time_sec']}s")
    print("==========================================================")
    print("[OK] Model training and evaluation completed successfully!")


if __name__ == "__main__":
    main()
