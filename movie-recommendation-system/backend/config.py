import os
import sys
from pathlib import Path

# Base Paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GRAPH_DATA_DIR = DATA_DIR / "graph"
MODELS_DIR = PROJECT_ROOT / "models"
ALS_MODEL_PATH = MODELS_DIR / "als_movie_model"
EVALUATION_METRICS_PATH = MODELS_DIR / "evaluation_metrics.json"

# Processed Dataset Files
RATINGS_CSV = PROCESSED_DATA_DIR / "ratings.csv"
MOVIES_CSV = PROCESSED_DATA_DIR / "movies.csv"
USERS_CSV = PROCESSED_DATA_DIR / "users.csv"
TRAIN_RATINGS_CSV = PROCESSED_DATA_DIR / "train_ratings.csv"
TEST_RATINGS_CSV = PROCESSED_DATA_DIR / "test_ratings.csv"

# GraphX Output Files
GRAPH_SUMMARY_JSON = GRAPH_DATA_DIR / "graph_summary.json"
DEGREE_DIST_JSON = GRAPH_DATA_DIR / "degree_distribution.json"
PAGERANK_NODES_JSON = GRAPH_DATA_DIR / "pagerank_nodes.json"
COMMUNITIES_JSON = GRAPH_DATA_DIR / "communities.json"
GRAPH_EDGES_SAMPLE_JSON = GRAPH_DATA_DIR / "graph_edges_sample.json"

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

# Spark Environment Configuration for Windows/Unix
PYTHON_EXE = sys.executable
os.environ["PYSPARK_PYTHON"] = PYTHON_EXE
os.environ["PYSPARK_DRIVER_PYTHON"] = PYTHON_EXE

# Java Home configuration for PySpark 4.x
if os.path.exists(r"C:\Program Files\Eclipse Adoptium\jdk-25.0.0.36-hotspot"):
    os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-25.0.0.36-hotspot"
    os.environ["PATH"] = os.path.join(os.environ["JAVA_HOME"], "bin") + os.pathsep + os.environ.get("PATH", "")

# Unset conflicting system SPARK_HOME for PySpark so it uses its own bundled Spark 4 jars
if "SPARK_HOME" in os.environ:
    del os.environ["SPARK_HOME"]
