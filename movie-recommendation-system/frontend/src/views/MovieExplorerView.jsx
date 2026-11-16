import React, { useEffect, useState } from "react";
import { 
  Search, Filter, Star, Eye, ChevronLeft, ChevronRight, Loader2, Sparkles, X, CheckCircle 
} from "lucide-react";
import { fetchMovies, fetchGenreAnalytics, predictRating } from "../api";

export default function MovieExplorerView() {
  const [movies, setMovies] = useState([]);
  const [genres, setGenres] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("All");
  const [minRating, setMinRating] = useState(0.0);
  const [sortBy, setSortBy] = useState("rating_count");

  // Predict Rating Modal State
  const [predictModalMovie, setPredictModalMovie] = useState(null);
  const [predictUserId, setPredictUserId] = useState(1);
  const [predictionResult, setPredictionResult] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [predictError, setPredictError] = useState(null);

  // Load genres once
  useEffect(() => {
    async function loadGenres() {
      try {
        const res = await fetchGenreAnalytics();
        setGenres(["All", ...(res.genres?.map(g => g.genre) || [])]);
      } catch (e) {
        console.error(e);
      }
    }
    loadGenres();
  }, []);

  // Fetch movies whenever filters/page change
  useEffect(() => {
    async function loadMovies() {
      try {
        setLoading(true);
        const res = await fetchMovies({
          query: searchQuery,
          genre: selectedGenre,
          min_rating: minRating,
          sort_by: sortBy,
          page,
          page_size: 18
        });
        setMovies(res.movies || []);
        setTotal(res.total || 0);
        setTotalPages(res.total_pages || 1);
      } catch (err) {
        console.error("Error loading movies:", err);
      } finally {
        setLoading(false);
      }
    }

    const timer = setTimeout(() => {
      loadMovies();
    }, 200);

    return () => clearTimeout(timer);
  }, [searchQuery, selectedGenre, minRating, sortBy, page]);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!predictModalMovie) return;
    try {
      setPredicting(true);
      setPredictError(null);
      const res = await predictRating(predictUserId, predictModalMovie.movieId);
      setPredictionResult(res);
    } catch (err) {
      setPredictError(err.message || "Failed to predict rating");
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Movie Catalog Explorer</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Browse, filter, and inspect {total.toLocaleString()} validated titles from the MovieLens dataset.
        </p>
      </div>

      {/* Control Filters Bar */}
      <div className="glass-panel p-5 rounded-2xl grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-gray-400" />
          <input
            type="text"
            placeholder="Search movie title..."
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
            className="w-full pl-10 pr-4 py-2 bg-gray-900/80 border border-gray-700/60 rounded-xl text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
          />
        </div>

        {/* Genre Selector */}
        <div>
          <select
            value={selectedGenre}
            onChange={(e) => { setSelectedGenre(e.target.value); setPage(1); }}
            className="w-full px-3.5 py-2 bg-gray-900/80 border border-gray-700/60 rounded-xl text-sm text-gray-200 focus:outline-none focus:border-purple-500 transition-colors"
          >
            {genres.map((g) => (
              <option key={g} value={g}>{g === "All" ? "All Genres" : g}</option>
            ))}
          </select>
        </div>

        {/* Min Rating Slider */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Min Rating:</span>
            <span className="font-semibold text-amber-400">{minRating.toFixed(1)} ★</span>
          </div>
          <input
            type="range"
            min="0.0"
            max="4.5"
            step="0.5"
            value={minRating}
            onChange={(e) => { setMinRating(parseFloat(e.target.value)); setPage(1); }}
            className="w-full accent-purple-500 bg-gray-800 rounded-lg cursor-pointer h-1.5"
          />
        </div>

        {/* Sort By Dropdown */}
        <div>
          <select
            value={sortBy}
            onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
            className="w-full px-3.5 py-2 bg-gray-900/80 border border-gray-700/60 rounded-xl text-sm text-gray-200 focus:outline-none focus:border-purple-500 transition-colors"
          >
            <option value="rating_count">Sort by Most Reviews</option>
            <option value="rating_desc">Sort by Highest Rated</option>
            <option value="title">Sort by Title (A-Z)</option>
            <option value="newest">Sort by Movie ID</option>
          </select>
        </div>
      </div>

      {/* Movie Cards Grid */}
      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3 text-purple-400">
          <Loader2 className="w-8 h-8 animate-spin" />
          <p className="text-gray-400 text-sm">Querying movie catalog...</p>
        </div>
      ) : movies.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl text-gray-400">
          <p className="text-base font-semibold">No movies found matching your filters.</p>
          <p className="text-xs mt-1 text-gray-500">Try loosening your search term or minimum rating threshold.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {movies.map((m) => (
            <div
              key={m.movieId}
              className="glass-panel p-5 rounded-2xl flex flex-col justify-between hover:border-purple-500/40 hover:scale-[1.01] transition-all duration-300"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="font-semibold text-white text-base leading-snug line-clamp-2">{m.title}</h3>
                  <span className="text-xs px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-300 font-mono shrink-0">
                    #{m.movieId}
                  </span>
                </div>

                <div className="flex flex-wrap gap-1.5 my-3">
                  {m.genres.split("|").map((g, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 text-[11px] font-medium rounded-full bg-white/5 text-gray-300 border border-white/10"
                    >
                      {g}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-3 border-t border-gray-800/80 flex items-center justify-between">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-1 text-amber-400 font-bold text-sm">
                    <Star className="w-4 h-4 fill-amber-400" />
                    <span>{m.avg_rating > 0 ? m.avg_rating : "Unrated"}</span>
                  </div>
                  <span className="text-[11px] text-gray-500 block">{m.rating_count} reviews</span>
                </div>

                <button
                  onClick={() => {
                    setPredictModalMovie(m);
                    setPredictionResult(null);
                    setPredictError(null);
                  }}
                  className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-purple-600/20 text-purple-300 hover:bg-purple-600 hover:text-white border border-purple-500/30 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5" /> Predict Rating
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-800">
          <span className="text-xs text-gray-400">
            Showing Page <span className="text-white font-semibold">{page}</span> of{" "}
            <span className="text-white font-semibold">{totalPages}</span> ({total.toLocaleString()} total movies)
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 rounded-xl bg-gray-900 border border-gray-700/60 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-purple-500/20 text-gray-200 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 rounded-xl bg-purple-500/10 border border-purple-500/30 text-xs font-semibold text-purple-300">
              {page}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-2 rounded-xl bg-gray-900 border border-gray-700/60 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-purple-500/20 text-gray-200 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Predict Rating Modal */}
      {predictModalMovie && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="glass-panel-glow w-full max-w-md p-6 rounded-3xl relative">
            <button
              onClick={() => setPredictModalMovie(null)}
              className="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-white/10"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <Sparkles className="w-4 h-4" /> Real-Time Inference
            </div>
            <h2 className="text-xl font-bold text-white mb-1">{predictModalMovie.title}</h2>
            <p className="text-xs text-gray-400 mb-5">{predictModalMovie.genres}</p>

            <form onSubmit={handlePredict} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Select User ID (1 - 943):
                </label>
                <input
                  type="number"
                  min="1"
                  max="943"
                  value={predictUserId}
                  onChange={(e) => setPredictUserId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={predicting}
                className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-semibold text-sm flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-purple-500/20 disabled:opacity-50"
              >
                {predicting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                Compute ALS Predicted Rating
              </button>
            </form>

            {predictionResult && (
              <div className="mt-5 p-4 rounded-2xl bg-purple-500/10 border border-purple-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-300">Predicted Score:</span>
                  <span className="text-xl font-extrabold text-amber-300 flex items-center gap-1">
                    <Star className="w-5 h-5 fill-amber-300" /> {predictionResult.predicted_rating} / 5.0
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Inference Latency:</span>
                  <span className="font-mono text-cyan-400">{predictionResult.latency_ms} ms</span>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Method:</span>
                  <span className="text-purple-300">{predictionResult.is_cold_start ? "Global Prior Fallback" : "ALS Latent Factor Dot Product"}</span>
                </div>
              </div>
            )}

            {predictError && (
              <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400">
                {predictError}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
