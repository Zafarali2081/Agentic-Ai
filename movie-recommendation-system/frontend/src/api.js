/**
 * CineGraph Frontend API Client
 */

const BASE_URL = "/api";

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error("Backend service unreachable");
  return res.json();
}

export async function fetchDashboardStats() {
  const res = await fetch(`${BASE_URL}/dashboard/stats`);
  if (!res.ok) throw new Error("Failed to load dashboard metrics");
  return res.json();
}

export async function fetchMovies(params = {}) {
  const query = new URLSearchParams();
  if (params.query) query.append("query", params.query);
  if (params.genre && params.genre !== "All") query.append("genre", params.genre);
  if (params.min_rating) query.append("min_rating", params.min_rating);
  if (params.sort_by) query.append("sort_by", params.sort_by);
  if (params.page) query.append("page", params.page);
  if (params.page_size) query.append("page_size", params.page_size);

  const res = await fetch(`${BASE_URL}/movies?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch movies");
  return res.json();
}

export async function fetchPopularMovies(limit = 10) {
  const res = await fetch(`${BASE_URL}/movies/popular?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch popular movies");
  return res.json();
}

export async function fetchTopRatedMovies(limit = 10, minRatings = 20) {
  const res = await fetch(`${BASE_URL}/movies/top-rated?limit=${limit}&min_ratings=${minRatings}`);
  if (!res.ok) throw new Error("Failed to fetch top-rated movies");
  return res.json();
}

export async function fetchGenreAnalytics() {
  const res = await fetch(`${BASE_URL}/analytics/genres`);
  if (!res.ok) throw new Error("Failed to fetch genre analytics");
  return res.json();
}

export async function fetchUserAnalytics() {
  const res = await fetch(`${BASE_URL}/analytics/users`);
  if (!res.ok) throw new Error("Failed to fetch user behavior analytics");
  return res.json();
}

export async function fetchGraphAnalytics() {
  const res = await fetch(`${BASE_URL}/analytics/graph`);
  if (!res.ok) throw new Error("Failed to fetch GraphX analytics");
  return res.json();
}

export async function fetchUserPreferences(userId) {
  const res = await fetch(`${BASE_URL}/analytics/user/${userId}/preferences`);
  if (!res.ok) throw new Error(`User ${userId} not found`);
  return res.json();
}

export async function fetchRecommendations(userId, algorithm = "als", k = 10, excludeRated = true) {
  const query = new URLSearchParams({
    algorithm,
    k: k.toString(),
    exclude_rated: excludeRated.toString()
  });
  const res = await fetch(`${BASE_URL}/recommendations/${userId}?${query.toString()}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to generate recommendations");
  }
  return res.json();
}

export async function fetchSimilarUsers(userId, topN = 5) {
  const res = await fetch(`${BASE_URL}/recommendations/${userId}/similar?top_n=${topN}`);
  if (!res.ok) throw new Error("Failed to find similar users");
  return res.json();
}

export async function predictRating(userId, movieId) {
  const res = await fetch(`${BASE_URL}/predict-rating`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: parseInt(userId), movie_id: parseInt(movieId) })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Prediction request failed");
  }
  return res.json();
}

export async function fetchModelEvaluation() {
  const res = await fetch(`${BASE_URL}/model/evaluation`);
  if (!res.ok) throw new Error("Model evaluation metrics not found");
  return res.json();
}

export async function triggerModelTraining(params = { rank: 10, max_iter: 15, reg_param: 0.1 }) {
  const res = await fetch(`${BASE_URL}/model/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params)
  });
  if (!res.ok) throw new Error("Model training initiation failed");
  return res.json();
}
