import React, { useState, useEffect } from "react";
import { 
  Sparkles, Star, User, Film, Info, ArrowRight, Loader2, CheckCircle2, TrendingUp, Cpu 
} from "lucide-react";
import { fetchRecommendations } from "../api";

export default function RecommendationsView() {
  const [userId, setUserId] = useState(1);
  const [algorithm, setAlgorithm] = useState("als");
  const [excludeRated, setExcludeRated] = useState(true);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Compare mode
  const [compareMode, setCompareMode] = useState(false);
  const [alsRecs, setAlsRecs] = useState([]);
  const [popRecs, setPopRecs] = useState([]);
  const [compareLoading, setCompareLoading] = useState(false);

  const handleGenerate = async (e) => {
    if (e) e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const res = await fetchRecommendations(userId, algorithm, 10, excludeRated);
      setData(res);
    } catch (err) {
      setError(err.message || "Failed to generate recommendations");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    try {
      setCompareLoading(true);
      setError(null);
      const [alsRes, popRes] = await Promise.all([
        fetchRecommendations(userId, "als", 10, excludeRated),
        fetchRecommendations(userId, "popularity", 10, excludeRated)
      ]);
      setAlsRecs(alsRes.recommendations || []);
      setPopRecs(popRes.recommendations || []);
      setCompareMode(true);
    } catch (err) {
      setError(err.message || "Failed to run comparison");
    } finally {
      setCompareLoading(false);
    }
  };

  useEffect(() => {
    handleGenerate();
  }, [algorithm]);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20 mb-3">
          <Cpu className="w-3.5 h-3.5" /> Spark MLlib Matrix Factorization (ALS)
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Personalized Movie Recommendations</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Generate top 10 recommended movies tailored to user interaction history with explainable AI rationales.
        </p>
      </div>

      {/* Control Panel Card */}
      <div className="glass-panel p-6 rounded-2xl">
        <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          {/* User ID Input */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-2 flex items-center gap-1.5">
              <User className="w-4 h-4 text-purple-400" /> Target User ID:
            </label>
            <input
              type="number"
              min="1"
              max="943"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700/70 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
              required
            />
          </div>

          {/* Algorithm Selector */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-2">
              Recommendation Engine:
            </label>
            <select
              value={algorithm}
              onChange={(e) => { setAlgorithm(e.target.value); setCompareMode(false); }}
              className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700/70 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
            >
              <option value="als">Spark MLlib ALS Collaborative Filtering</option>
              <option value="popularity">Bayesian Popularity Baseline</option>
            </select>
          </div>

          {/* Negative Filter Checkbox */}
          <div className="flex items-center gap-2.5 pb-3">
            <input
              type="checkbox"
              id="excludeRated"
              checked={excludeRated}
              onChange={(e) => setExcludeRated(e.target.checked)}
              className="w-4 h-4 rounded accent-purple-500 cursor-pointer"
            />
            <label htmlFor="excludeRated" className="text-xs text-gray-300 font-medium cursor-pointer">
              Exclude already watched movies
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-semibold text-sm flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-purple-500/20 disabled:opacity-50 transition-all"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Generate
            </button>

            <button
              type="button"
              onClick={handleCompare}
              disabled={compareLoading}
              className="py-2.5 px-3 rounded-xl bg-white/5 hover:bg-white/10 border border-gray-700 text-gray-200 text-xs font-semibold flex items-center gap-1.5 cursor-pointer transition-all"
              title="Compare ALS vs Popularity side-by-side"
            >
              {compareLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4 text-cyan-400" />}
              Compare
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="glass-panel p-5 rounded-2xl border-red-500/40 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Side-by-Side Comparison Mode */}
      {compareMode ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              Side-by-Side Comparison for User {userId}
            </h2>
            <button
              onClick={() => setCompareMode(false)}
              className="text-xs text-purple-400 hover:underline cursor-pointer"
            >
              Return to single view
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* ALS Recommender Column */}
            <div className="glass-panel p-5 rounded-2xl border-purple-500/30">
              <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-800">
                <span className="font-bold text-sm text-purple-300">Spark MLlib ALS (Collaborative Filtering)</span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300">Personalized</span>
              </div>
              <div className="space-y-3">
                {alsRecs.map((m, idx) => (
                  <div key={m.movieId} className="p-3 rounded-xl bg-white/5 flex items-center justify-between">
                    <div className="max-w-[75%]">
                      <div className="font-medium text-sm text-white truncate">{idx + 1}. {m.title}</div>
                      <div className="text-[11px] text-gray-400 truncate">{m.genres}</div>
                      <div className="text-[10px] text-purple-300 mt-1 italic">{m.rationale}</div>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-bold text-amber-300 flex items-center gap-1 justify-end">
                        <Star className="w-3.5 h-3.5 fill-amber-300" /> {m.predicted_rating}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Popularity Baseline Column */}
            <div className="glass-panel p-5 rounded-2xl border-blue-500/30">
              <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-800">
                <span className="font-bold text-sm text-blue-300">Popularity Baseline (Bayesian-Weighted)</span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300">Global Consensus</span>
              </div>
              <div className="space-y-3">
                {popRecs.map((m, idx) => (
                  <div key={m.movieId} className="p-3 rounded-xl bg-white/5 flex items-center justify-between">
                    <div className="max-w-[75%]">
                      <div className="font-medium text-sm text-white truncate">{idx + 1}. {m.title}</div>
                      <div className="text-[11px] text-gray-400 truncate">{m.genres}</div>
                      <div className="text-[10px] text-blue-300 mt-1 italic">{m.rationale}</div>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-bold text-blue-300 flex items-center gap-1 justify-end">
                        <Star className="w-3.5 h-3.5 fill-blue-300" /> {m.predicted_rating}
                      </span>
                      <span className="text-[10px] text-gray-400 block">{m.popularity_score} score</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Single View Mode */
        data && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-400" />
                Top 10 Recommendations for User {data.userId}
              </h2>
              <span className="text-xs px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300">
                {data.algorithm}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.recommendations.map((m, idx) => (
                <div
                  key={m.movieId}
                  className="glass-panel p-5 rounded-2xl flex flex-col justify-between hover:border-purple-500/30 transition-all duration-300"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex items-start gap-2">
                        <span className="flex items-center justify-center w-6 h-6 rounded-lg bg-purple-500/20 text-purple-300 font-bold text-xs shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <div>
                          <h3 className="font-bold text-white text-base leading-snug">{m.title}</h3>
                          <p className="text-xs text-gray-400 mt-0.5">{m.genres}</p>
                        </div>
                      </div>

                      <div className="text-right shrink-0">
                        <div className="flex items-center gap-1 font-extrabold text-amber-300 text-base">
                          <Star className="w-4 h-4 fill-amber-300" />
                          <span>{m.predicted_rating}</span>
                        </div>
                        <span className="text-[10px] text-gray-500 uppercase tracking-wider block">Predicted</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-800/80 flex items-center gap-2 text-xs text-purple-300/90 bg-purple-500/5 px-3 py-2 rounded-xl">
                    <Info className="w-4 h-4 shrink-0 text-purple-400" />
                    <span className="italic">{m.rationale}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      )}
    </div>
  );
}
