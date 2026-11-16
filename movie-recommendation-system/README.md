# CineGraph: Movie Recommendation & User Preference Analysis

[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5%20%7C%204.2-E25A1C?logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![GraphX](https://img.shields.io/badge/Graph%20Analytics-Scala%20GraphX-DC322F)](https://spark.apache.org/graphx/)
[![Spark MLlib](https://img.shields.io/badge/ML-Spark%20MLlib%20ALS-FF6F00)](https://spark.apache.org/mllib/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Tailwind-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Tests-20%20Passed-brightgreen)](https://docs.pytest.org/)

**CineGraph** is an academic-grade, end-to-end distributed Big Data analytics and movie recommendation platform. The project demonstrates distributed data processing with **PySpark**, bipartite graph mining and community detection using **Apache Spark GraphX (Scala)**, matrix factorization collaborative filtering using **Spark MLlib ALS**, an asynchronous REST backend powered by **FastAPI**, and a dark glassmorphic visualization dashboard built in **React** with **Cytoscape.js** and **Recharts**.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement & Objectives](#problem-statement--objectives)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Dataset Description](#dataset-description)
6. [Installation & Environment Setup](#installation--environment-setup)
7. [Step-by-Step Execution Guide](#step-by-step-execution-guide)
8. [REST API Documentation](#rest-api-documentation)
9. [GraphX Analytics Engine](#graphx-analytics-engine)
10. [Recommendation Engine & Empirical Evaluation](#recommendation-engine--empirical-evaluation)
11. [Frontend Dashboard Views](#frontend-dashboard-views)
12. [Automated Testing Suite](#automated-testing-suite)
13. [Future Enhancements](#future-enhancements)

---

## 1. Project Overview
Modern movie recommendation systems require scalable distributed computing infrastructures to handle millions of interaction events, uncover hidden topological community clusters, and deliver low-latency personalized recommendations. CineGraph bridges heavy distributed batch analytics with sub-millisecond API inference.

---

## 2. Problem Statement & Objectives

### Problem Statement
Standard recommender systems face:
- Scalability bottlenecks when dealing with high-dimensional interaction matrices.
- The cold-start dilemma for sparse users and newly ingested movies.
- Ignorance of structural influence (e.g., distinguishing popular central titles in interaction graphs from titles with artificially inflated small-sample ratings).

### Project Objectives
1. **Distributed Data Processing**: Ingest, clean, validate, and aggregate MovieLens interactions using PySpark DataFrames and Spark SQL.
2. **Graph Analytics via Scala GraphX**: Construct a bipartite User-Movie network with collision-free vertex namespaces; compute In/Out degrees, Connected Components, PageRank structural prestige, and Label Propagation Communities (LPA).
3. **Machine Learning Recommendation**: Train a Spark MLlib Alternating Least Squares (ALS) collaborative filtering model with negative filtering and cold-start fallback.
4. **Empirical Benchmarking**: Evaluate models against a Bayesian-weighted popularity baseline using RMSE, MAE, Precision@K, Recall@K, and execution latency.
5. **Interactive UI**: Deliver an interactive glassmorphic analytics dashboard with Cytoscape.js network rendering and Recharts data visualizations.

---

## 3. System Architecture

```
                                  +---------------------------------------+
                                  |     GroupLens MovieLens Repository    |
                                  +---------------------------------------+
                                                      |
                                           [download_dataset.py]
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |           data/raw/ml-100k/           |
                                  +---------------------------------------+
                                                      |
                                           [preprocess_data.py]
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       data/processed/*.csv            |
                                  |  (ratings, movies, users, train, test)|
                                  +---------------------------------------+
                                           |                      |
               +---------------------------+                      +---------------------------+
               |                                                                              |
               v                                                                              v
+-------------------------------+                                              +-------------------------------+
|     PySpark Engine            |                                              |  Scala Apache Spark GraphX    |
| - DataFrame Transformations   |                                              | - Bipartite Graph Construction|
| - Spark SQL Aggregations      |                                              | - In/Out Degree Centrality    |
| - Genre & Temporal Analytics  |                                              | - PageRank Influence          |
+-------------------------------+                                              | - Connected Components        |
               |                                                               | - Community Detection (LPA)   |
               v                                                               +-------------------------------+
+-------------------------------+                                                              |
|   Spark MLlib ALS Engine      |                                                              v
| - Matrix Factorization        |                                              +-------------------------------+
| - Cold Start Fallback         |                                              |     data/graph/*.json         |
| - Evaluation (RMSE, MAE, P@K) |                                              |  (summary, degree, communities|
+-------------------------------+                                              |   pagerank, subgraph edges)   |
               |                                                               +-------------------------------+
               |                                                                               |
               +--------------------------------------+----------------------------------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |     FastAPI REST Backend      |
                                      |  - Pydantic Validation        |
                                      |  - In-Memory Latent Cache     |
                                      |  - Swagger Interactive Docs   |
                                      +-------------------------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |   CineGraph React Dashboard   |
                                      |  - Cytoscape.js Canvas        |
                                      |  - Recharts Visualizations    |
                                      |  - 6 Modular Analytics Views  |
                                      +-------------------------------+
```

---

## 4. Technology Stack

| Layer | Technologies | Role |
| :--- | :--- | :--- |
| **Big Data Distributed Processing** | Apache Spark 3.5 / 4.2, PySpark, Spark SQL | Distributed DataFrame transformations, joins, and aggregations |
| **Graph Analytics** | Scala 2.12, Apache Spark GraphX | Bipartite user-movie network modeling, PageRank, LPA communities |
| **Machine Learning** | Spark MLlib ALS, NumPy, Scikit-learn | Latent factor collaborative filtering, Bayesian popularity baseline |
| **Backend API** | Python 3.13, FastAPI, Uvicorn, Pydantic | High-performance asynchronous REST API with in-memory factor caching |
| **Frontend UI** | React 19, Vite, Tailwind CSS v4, Lucide Icons | Responsive glassmorphic analytics interface |
| **Visualizations** | Recharts, Cytoscape.js | Network graph exploration, interactive metric curves |
| **Testing** | Pytest, FastAPI TestClient | 20 automated unit and integration tests |

---

## 5. Dataset Description

The application processes the **MovieLens 100K** dataset published by GroupLens Research at the University of Minnesota, structured to maintain full forward compatibility with MovieLens 1M and 20M datasets:

- **ratings.csv** (100,000 records): `userId` (1-943), `movieId` (1-1682), `rating` (0.5-5.0), `timestamp`, `datetime` (UTC ISO).
- **movies.csv** (1,682 titles): `movieId`, `title`, `genres` (pipe-delimited string of 18 categories).
- **users.csv** (943 user profiles): `userId`, `age`, `gender`, `occupation`, `zip_code`.
- **train_ratings.csv** (80,367 records, 80% split): Seeded stratified train partition.
- **test_ratings.csv** (19,633 records, 20% split): Held-out test split for quantitative benchmarking.

---

## 6. Installation & Environment Setup

### Prerequisites
- **Python**: 3.10+ (Verified on Python 3.13)
- **Java**: Java JDK 8 or Java 17+ (Adoptium Temurin OpenJDK)
- **Apache Spark**: Spark 3.5.x with GraphX
- **Node.js**: v18+ (Verified on Node v24) & npm

### Clone and Install Backend Dependencies
```bash
git clone <repository_url>
cd movie-recommendation-system

# Install Python packages
py -3 -m pip install -r backend/requirements.txt
```

### Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 7. Step-by-Step Execution Guide

### Step 1: Download MovieLens Dataset
Automatically downloads and extracts the official dataset from GroupLens:
```powershell
py -3 scripts/download_dataset.py
```

### Step 2: Preprocess & Validate Dataset
Cleans records, removes duplicates, validates rating boundaries, extracts genres, and generates reproducible train/test splits:
```powershell
py -3 scripts/preprocess_data.py
```

### Step 3: Run Scala Apache Spark GraphX Engine
Compiles `MovieGraphAnalytics.scala` and executes bipartite graph analytics on Spark:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_graphx.ps1
# On Linux/macOS:
# bash scripts/run_graphx.sh
```

### Step 4: Train Spark MLlib ALS Recommendation Engine
Trains the collaborative filtering model, fits the baseline, and writes evaluation metrics:
```powershell
py -3 scripts/train_model.py
```

### Step 5: Start the FastAPI Backend Server
```powershell
py -3 backend/main.py
# Server starts at http://127.0.0.1:8000
# Interactive Swagger Documentation: http://127.0.0.1:8000/docs
```

### Step 6: Start the React Dashboard
In a separate terminal:
```powershell
cd frontend
npm run dev
# Dashboard launches at http://localhost:5173
```

---

## 8. REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health status of Spark, ALS model, and GraphX artifacts |
| `GET` | `/api/dashboard/stats` | Global metrics, rating volume distributions, monthly activity |
| `GET` | `/api/movies` | Paginated movie browsing with query, genre, and rating filters |
| `GET` | `/api/movies/popular` | Top N movies by total review count |
| `GET` | `/api/movies/top-rated` | Top N movies by average rating (min 20 reviews) |
| `GET` | `/api/analytics/genres` | Aggregated rating volume and average stars per genre |
| `GET` | `/api/analytics/users` | User engagement tiers (Casual, Active, Power User) |
| `GET` | `/api/analytics/graph` | GraphX metrics: degrees, PageRank, LPA communities, subgraph |
| `GET` | `/api/recommendations/{user_id}` | Top 10 personalized recommendations with explainable AI rationales |
| `GET` | `/api/recommendations/{user_id}/similar` | Similar users computed via cosine similarity on ALS latent vectors |
| `POST` | `/api/predict-rating` | Predict user rating for a movie (`{"user_id": 1, "movie_id": 50}`) |
| `GET` | `/api/model/evaluation` | Full evaluation metrics comparison (RMSE, MAE, Precision, Recall) |
| `POST` | `/api/model/train` | Trigger asynchronous ALS model retraining with custom hyperparameters |

### Sample API Request & Response
```bash
POST /api/predict-rating
Content-Type: application/json

{
  "user_id": 1,
  "movie_id": 50
}
```
**Response (200 OK, Latency: 0.15ms):**
```json
{
  "userId": 1,
  "movieId": 50,
  "movie_title": "Star Wars (1977)",
  "genres": "Action|Adventure|Romance|Sci-Fi|War",
  "predicted_rating": 4.36,
  "is_cold_start": false,
  "latency_ms": 0.152
}
```

---

## 9. GraphX Analytics Engine

Constructed in genuine Scala using `org.apache.spark.graphx._`:
- **Collision-Free Namespace**: User Vertex ID = `userId`; Movie Vertex ID = `1,000,000 + movieId`.
- **PageRank vs Rating Quality**: PageRank measures structural centrality within the interaction topology (frequently linked to high-degree reviewer nodes), explaining why titles like *Star Wars (1977)* and *Fargo (1996)* achieve the highest PageRank influence scores.
- **Label Propagation Algorithm (LPA)**: Unsupervised clustering partitions users and movies into cohesive taste communities.

---

## 10. Recommendation Engine & Empirical Evaluation

### Quantitative Benchmarking Matrix (Evaluated on 19,633 Held-Out Ratings)

| Evaluation Metric | Spark MLlib ALS | Popularity Baseline | Relative Improvement | Winning Model |
| :--- | :---: | :---: | :---: | :---: |
| **RMSE (Root Mean Squared Error)** | **0.9234** | 1.0026 | **+7.90%** | **ALS** |
| **MAE (Mean Absolute Error)** | **0.7293** | 0.8004 | **+8.88%** | **ALS** |
| **Precision@10 (Relevance $\ge$ 4.0)** | **64.04%** | 53.42% | **+19.88%** | **ALS** |
| **Recall@10** | **71.26%** | 61.10% | **+16.63%** | **ALS** |
| **Inference Latency** | **< 1.0 ms** | < 0.2 ms | - | - |

---

## 11. Frontend Dashboard Views

1. **Dashboard Overview**: Global KPI cards, ratings distribution bar chart, monthly activity timeline, and top 10 popular movies.
2. **Movie Explorer**: Full catalog with debounced keyword search, multi-genre filtering, minimum star rating slider, and live rating prediction modals.
3. **Personalized Recommendations**: Top 10 recommendations per user with explainable AI rationales and side-by-side comparison mode against the baseline.
4. **Graph Analytics**: Interactive **Cytoscape.js** canvas rendering the bipartite user-movie graph with node inspection drawers, PageRank influence tables, and LPA community summaries.
5. **Model Performance**: Quantitative benchmarks, RMSE/MAE cards, Precision@K / Recall@K curves, actual vs. predicted distribution charts, and a real-time hyperparameter tuning form.
6. **User Preference Analysis**: Individualized rating distributions, favorite genre affinities, rating history, and taste-alike peer user recommendations.

---

## 12. Automated Testing Suite

The project includes 20 comprehensive unit and integration tests covering the data pipeline, recommendation models, and REST endpoints:
```powershell
py -3 -m pytest tests/ -v
```

```
tests/test_api.py::test_health_endpoint PASSED                           [  5%]
tests/test_api.py::test_dashboard_stats PASSED                           [ 10%]
tests/test_api.py::test_movies_list PASSED                               [ 15%]
tests/test_api.py::test_movie_search PASSED                              [ 20%]
tests/test_api.py::test_graph_analytics PASSED                           [ 25%]
tests/test_api.py::test_recommendations_als PASSED                       [ 30%]
tests/test_api.py::test_recommendations_popularity PASSED                [ 35%]
tests/test_api.py::test_predict_rating PASSED                            [ 40%]
tests/test_api.py::test_similar_users PASSED                             [ 45%]
tests/test_api.py::test_model_evaluation PASSED                          [ 50%]
tests/test_preprocessing.py::test_processed_files_exist PASSED           [ 55%]
tests/test_preprocessing.py::test_ratings_schema_and_boundaries PASSED   [ 60%]
tests/test_preprocessing.py::test_movies_schema_and_genres PASSED        [ 65%]
tests/test_preprocessing.py::test_clean_and_validate_logic PASSED        [ 70%]
tests/test_preprocessing.py::test_train_test_split_ratio PASSED          [ 75%]
tests/test_recommendation.py::test_als_factors_loaded PASSED             [ 80%]
tests/test_recommendation.py::test_als_prediction PASSED                 [ 85%]
tests/test_recommendation.py::test_als_recommend_top_k PASSED            [ 90%]
tests/test_recommendation.py::test_als_similar_users PASSED              [ 95%]
tests/test_recommendation.py::test_popularity_recommender PASSED         [100%]

======================= 20 passed in 11.76s =======================
```

---

## 13. Future Enhancements
- Integration of Graph Neural Networks (GNNs) using PyTorch Geometric on the bipartite graph.
- Real-time online streaming recommendation updates using Apache Spark Structured Streaming with Kafka.
- Content-based hybrid filtering incorporating natural language movie plot embeddings from BERT/Sentence-Transformers.
