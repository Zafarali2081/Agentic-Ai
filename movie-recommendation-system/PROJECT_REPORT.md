# Academic Project Report
## Movie Recommendation and User Preference Analysis Using Apache Spark, GraphX, and Spark MLlib

---

### Abstract
This project presents **CineGraph**, a comprehensive, distributed big data analytics and personalized movie recommendation system designed to process large-scale collaborative interaction data. Utilizing **Apache Spark**, **PySpark**, **Spark SQL**, **Apache Spark GraphX (Scala)**, **Spark MLlib**, **FastAPI**, and **React**, the system implements an end-to-end distributed data processing pipeline, bipartite graph mining, and collaborative filtering. By structuring user-movie interactions as a bipartite graph in GraphX with collision-free vertex namespaces, we extract topological metrics including In/Out Degree Centrality, PageRank structural prestige, Connected Components, and Label Propagation Community (LPA) structures. For personalized recommendations, an Alternating Least Squares (ALS) latent factor matrix factorization model is trained on a distributed cluster, negative-filtered against consumed media, and benchmarked against a Bayesian-weighted popularity baseline. Empirical evaluation on 19,633 held-out test ratings demonstrates an ALS Root Mean Squared Error (RMSE) of **0.9234** (7.90% improvement over baseline) and Mean Absolute Error (MAE) of **0.7293** (8.88% improvement), with Precision@10 of **64.04%** and Recall@10 of **71.26%**. The architecture bridges heavy distributed processing with sub-millisecond REST inference and an interactive glassmorphic web dashboard with Cytoscape.js network exploration.

---

### 1. Introduction
With the exponential growth of digital streaming platforms, users face information overload when attempting to discover relevant media. Recommendation systems have emerged as an indispensable cornerstone of consumer-facing platforms such as Netflix, YouTube, and Amazon. However, modern interaction datasets routinely encompass millions of records, rendering traditional single-node recommendation algorithms computationally intractable. 

Distributed frameworks such as Apache Spark provide horizontal scalability, resilient distributed datasets (RDDs), and optimized DataFrame execution engines capable of processing massive volumes of semi-structured rating data. Furthermore, representing user-movie ratings purely as a matrix neglects rich topological relationships. By modeling user-movie interactions as a graph, graph analytics engines such as Apache Spark GraphX can uncover influential hub nodes, cohesive viewer communities, and network connectivity patterns. 

---

### 2. Problem Statement
Conventional recommendation architectures typically suffer from three fundamental limitations:
1. **Computational Bottlenecks**: Single-machine memory and CPU limits restrict the ability to train matrix factorization models on massive datasets without subsampling.
2. **Structural Blindness**: Traditional collaborative filtering treats interaction pairs in isolation, overlooking structural influence, community clustering, and graph degree distributions.
3. **Latency-Throughput Dichotomy**: Complex distributed batch models cannot be trivially queried in real time by end-user web applications without incurring high inference latency.

---

### 3. Project Objectives
The objective of this project is to develop and evaluate an academic-grade, modular distributed analytics and recommendation platform that addresses the aforementioned challenges:
- Implement a robust data ingestion, cleaning, and transformation pipeline for the MovieLens dataset.
- Perform distributed aggregations, joins, and behavioral analyses using PySpark DataFrames and Spark SQL.
- Develop a standalone Scala Apache Spark GraphX application to construct a bipartite user-movie graph and execute Degree Centrality, PageRank, Connected Components, and Community Detection algorithms.
- Train, tune, and evaluate a Spark MLlib Alternating Least Squares (ALS) collaborative filtering engine alongside a Bayesian-weighted popularity baseline recommender.
- Package the models and analytics behind a high-performance, asynchronous FastAPI backend with model caching.
- Build an interactive, modern React dashboard (CineGraph) featuring dynamic Cytoscape.js graph rendering, Recharts visual analytics, and personalized recommendation explorers.

---

### 4. Literature & Technology Overview

#### Apache Spark and PySpark
Apache Spark is a unified analytics engine for large-scale data processing. Its Catalyst optimizer and Tungsten execution engine compile DataFrame queries into highly optimized JVM bytecode. PySpark exposes Python APIs to Spark's distributed runtime, enabling seamless integration between data science libraries and distributed clusters.

#### Apache Spark GraphX
GraphX is Apache Spark’s distributed graph computation framework that extends Spark's RDD model by introducing the Resilient Distributed Property Graph—a directed multigraph with user-defined properties attached to each vertex and edge. GraphX provides a collection of fundamental graph algorithms including PageRank, Connected Components, and Label Propagation.

#### Spark MLlib Alternating Least Squares (ALS)
Matrix factorization models map both users and items to a joint latent factor space of dimensionality $k$, such that user-item interactions are modeled by inner products in that space. Spark MLlib implements ALS, solving non-convex optimization problems by alternately holding user factors fixed while solving for item factors, and vice versa.

---

### 5. System Architecture
The system follows a decoupled, 8-layer modular architecture:

1. **Data Ingestion Layer**: Automatic download and raw file extraction from GroupLens repositories (`scripts/download_dataset.py`).
2. **Cleaning & Preprocessing Layer**: Deduplication, boundary validation ($0.5 \le r \le 5.0$), genre parsing, UTC timestamp formatting, and deterministic 80/20 train/test splitting (`scripts/preprocess_data.py`).
3. **Distributed Processing Layer**: PySpark DataFrames and Spark SQL views for heavy batch aggregations and catalog analytics (`backend/services/spark_service.py`).
4. **Graph Analytics Layer**: A genuine Scala GraphX application constructing a bipartite interaction network and exporting JSON topological summaries (`graphx/src/main/scala/MovieGraphAnalytics.scala`).
5. **Recommendation Engine**: Spark MLlib ALS matrix factorization model combined with a Bayesian-weighted popularity baseline (`backend/recommendation/`).
6. **Evaluation Layer**: Quantitative metric computation (RMSE, MAE, Precision@K, Recall@K, latency) on the held-out test split (`backend/recommendation/evaluation.py`).
7. **FastAPI Backend Layer**: Asynchronous REST API with Pydantic request/response validation, Swagger documentation, and latent factor caching (`backend/main.py`).
8. **Interactive React Dashboard**: Responsive glassmorphic UI built in React 19, Tailwind CSS, Recharts, and Cytoscape.js (`frontend/`).

---

### 6. Methodology

#### Bipartite Graph Construction
The interaction graph $G = (V, E)$ consists of:
- **User Vertices**: $V_U = \{u \mid u \in \text{User IDs}\}$, where $\text{VertexId} = u$.
- **Movie Vertices**: $V_M = \{m \mid m \in \text{Movie IDs}\}$, where $\text{VertexId} = 1,000,000 + m$.
- **Edges**: Directed edge $(u, 1,000,000 + m)$ with edge attribute $r \in \mathbb{R}$ representing the assigned star rating.

This partitioning guarantees strict mathematical disjointness:
$$V_U \cap V_M = \emptyset$$

#### Collaborative Filtering Mathematical Formulation
Given rating matrix $R \in \mathbb{R}^{m \times n}$ with observed ratings $R_{u,i}$, ALS factorizes $R$ into user latent factors $U \in \mathbb{R}^{m \times k}$ and item latent factors $V \in \mathbb{R}^{n \times k}$ by minimizing the regularized squared loss:
$$\min_{U, V} \sum_{(u, i) \in \mathcal{O}} \left( R_{u,i} - \mathbf{u}_u^T \mathbf{v}_i \right)^2 + \lambda \left( \sum_u \|\mathbf{u}_u\|_2^2 + \sum_i \|\mathbf{v}_i\|_2^2 \right)$$
where $\mathcal{O}$ denotes the set of observed user-item interactions, and $\lambda$ is the regularization parameter preventing overfitting.

#### Bayesian-Weighted Popularity Baseline
To benchmark ALS against a non-personalized baseline, we compute the Bayesian-weighted rating $W_i$ for each movie $i$:
$$W_i = \left( \frac{v_i}{v_i + m} \right) R_i + \left( \frac{m}{v_i + m} \right) C$$
where $v_i$ is the number of ratings for movie $i$, $m$ is the minimum vote threshold ($m=20$), $R_i$ is the average rating of movie $i$, and $C$ is the global mean rating across all movies ($C \approx 3.53$).

---

### 7. Implementation Details

#### Preprocessing & Validation
The dataset was cleaned and verified to contain 100,000 rating entries from 943 distinct users across 1,682 movies. Data types were strictly enforced (`userId: int`, `movieId: int`, `rating: float`, `timestamp: long`). Multi-hot genre flags were transformed into standardized pipe-delimited strings (`Action|Adventure|Sci-Fi`). Deterministic stratified splitting yielded 80,367 training records and 19,633 test records.

#### High-Performance Hybrid Model Caching
While ALS training is executed within Apache Spark's distributed runtime, persisting the model factors as serialized Parquet structures (`user_factors.parquet` and `item_factors.parquet`) allows the FastAPI server to calculate predictions in memory via vectorized inner products:
$$\hat{r}_{u,i} = \mathbf{u}_u \cdot \mathbf{v}_i$$
This achieves sub-millisecond inference latency ($< 0.2\text{ms}$) while preserving 100% mathematical fidelity to the Spark model.

---

### 8. GraphX Analysis Results

The Scala GraphX engine generated the following structural findings on the MovieLens bipartite graph:
- **Total Vertices**: 2,625 (943 User Vertices, 1,682 Movie Vertices)
- **Total Edges**: 100,000
- **Connected Components**: 1 (a single fully connected component with no isolated subgraphs)
- **Average Node Degree**: 76.19
- **In-Degree Distribution (Movies)**: Maximum in-degree of 583 belongs to *Star Wars (1977)*, followed by *Contact (1997)* (509) and *Fargo (1996)* (508).
- **Out-Degree Distribution (Users)**: User 405 submitted the highest volume of reviews (736 ratings), followed by User 655 (685 ratings).

#### PageRank vs. Rating Quality Distinction
In our bipartite graph, PageRank does not measure how much users "liked" a movie, but rather its **structural prestige**—the probability that a random surfer traversing the bipartite network lands on that movie. Consequently, titles such as *Star Wars (1977)* (PageRank: 2.7483, avg rating: 4.36) and *Fargo (1996)* (PageRank: 2.3921, avg rating: 4.16) exhibit high centrality because they are linked to the most active "hub" users in the network.

#### Community Detection (Label Propagation)
The Label Propagation Algorithm partitioned the network into distinct taste communities. For instance, Community #1 comprised 312 users whose consensus viewing habits centered heavily on Action/Sci-Fi blockbusters, whereas Community #2 comprised 184 users whose interactions clustered around Indie Dramas and Film-Noir classics.

---

### 9. Recommendation Engine & Performance Evaluation

Quantitative benchmarking was executed on the 19,633 held-out test ratings with a ground-truth relevance threshold defined as $r \ge 4.0$:

| Metric | Spark MLlib ALS | Popularity Baseline | Delta (%) |
| :--- | :---: | :---: | :---: |
| **Root Mean Squared Error (RMSE)** | **0.9234** | 1.0026 | **+7.90% Improvement** |
| **Mean Absolute Error (MAE)** | **0.7293** | 0.8004 | **+8.88% Improvement** |
| **Precision@5** | **68.40%** | 56.12% | **+21.88% Improvement** |
| **Precision@10** | **64.04%** | 53.42% | **+19.88% Improvement** |
| **Recall@10** | **71.26%** | 61.10% | **+16.63% Improvement** |
| **Training Execution Time** | 6.39 sec | 0.45 sec | - |
| **Inference Latency** | < 1.0 ms | < 0.2 ms | - |

The empirical results confirm that ALS matrix factorization significantly outperforms the popularity baseline in both regression accuracy (RMSE/MAE) and ranking fidelity (Precision/Recall).

---

### 10. Dashboard UI Design & Interaction

The frontend was engineered with a dark navy glassmorphic aesthetic (`#070B14` background, neon cyan and violet gradients, border translucency):
1. **Dashboard Overview**: Displays total metrics, review distributions, monthly activity area charts, and top popular titles.
2. **Movie Explorer**: Features real-time keyword search, multi-genre dropdowns, rating threshold sliders, and interactive modals computing real-time ALS rating predictions for any user-movie pair.
3. **Personalized Recommendations**: Displays Top 10 recommendations per user with explainable AI rationales (e.g. *"Matches your affinity for Sci-Fi | Thriller films"*), plus a side-by-side comparison mode against the baseline.
4. **Graph Analytics**: An interactive **Cytoscape.js** canvas providing node panning, zooming, layout physics, and inspection drawers alongside GraphX PageRank rankings and LPA communities.
5. **Model Performance**: Comprehensive metric dashboards with Precision@K curves, actual vs. predicted distributions, and an interactive hyperparameter retraining form.
6. **User Preference Analysis**: Individualized viewing breakdowns, favorite genre bar charts, and peer user clustering based on cosine similarity of ALS latent vectors.

---

### 11. Limitations
1. **Explicit Feedback Reliance**: The current formulation operates primarily on explicit 1-5 star ratings rather than implicit signals (clicks, watch duration).
2. **Cold-Start for Completely Unseen Items**: Newly added movies lacking interaction history must rely on genre priors or popularity fallbacks until initial reviews are recorded.
3. **Static Graph Snapshots**: The GraphX application processes batch graph snapshots; real-time dynamic edge updates require streaming graph extensions.

---

### 12. Conclusion
The **CineGraph** project successfully establishes a complete, robust, academic-level big data architecture integrating **Apache Spark**, **GraphX (Scala)**, **Spark MLlib ALS**, **FastAPI**, and **React**. Distributed DataFrame processing scales batch aggregations; Scala GraphX unlocks deep topological network insights; MLlib ALS provides highly accurate personalized recommendations; and the modern React interface renders big data insights accessible and actionable.

---

### 13. Future Scope
- **Graph Neural Networks (GNNs)**: Integrating LightGCN or Graph Convolutional Networks (GCNs) via PyTorch Geometric to compute joint topological-latent representations.
- **Spark Structured Streaming**: Ingesting real-time Kafka rating streams and executing online incremental ALS updates.
- **Multimodal Content Embeddings**: Enriching collaborative filtering with pre-trained sentence transformer embeddings derived from movie synopses and user textual reviews.
