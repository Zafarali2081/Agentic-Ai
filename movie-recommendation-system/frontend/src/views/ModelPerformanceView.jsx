import React, { useEffect, useState } from "react";
import { 
  Cpu, Award, Activity, CheckCircle, TrendingUp, Sliders, RefreshCw, Loader2, Sparkles, AlertCircle 
} from "lucide-react";
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  CartesianGrid, Legend, ScatterChart, Scatter, ZAxis 
} from "recharts";
import { fetchModelEvaluation, triggerModelTraining } from "../api";

export default function ModelPerformanceView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Retrain form state
  const [rank, setRank] = useState(10);
  const [maxIter, setMaxIter] = useState(15);
  const [regParam, setRegParam] = useState(0.1);
  const [retraining, setRetraining] = useState(false);
  const [retrainMsg, setRetrainMsg] = useState(null);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetchModelEvaluation();
      setData(res);
      if (res.model_metadata) {
        setRank(res.model_metadata.rank || 10);
        setMaxIter(res.model_metadata.max_iter || 15);
        setRegParam(res.model_metadata.reg_param || 0.1);
      }
    } catch (err) {
      setError(err.message || "Failed to load model evaluation metrics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  const handleRetrain = async (e) => {
    e.preventDefault();
    try {
      setRetraining(true);
      setRetrainMsg(null);
      const res = await triggerModelTraining({ rank: parseInt(rank), max_iter: parseInt(maxIter), reg_param: parseFloat(regParam) });
      setRetrainMsg("Spark MLlib training initiated in background. Refreshing in 10s...");
      setTimeout(() => {
        loadMetrics();
        setRetraining(false);
        setRetrainMsg("Model retrained and evaluation metrics updated successfully!");
      }, 10000);
    } catch (err) {
      setRetrainMsg(`Training failed: ${err.message}`);
      setRetraining(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3 text-purple-400">
        <Loader2 className="w-10 h-10 animate-spin" />
        <p className="text-gray-400 font-medium">Loading Spark MLlib evaluation benchmarks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel p-6 rounded-2xl border-red-500/30 text-red-400">
        <p className="font-semibold">Model Evaluation Not Ready:</p>
        <p className="text-sm text-gray-400 mt-1">{error}</p>
        <button
          onClick={loadMetrics}
          className="mt-4 px-4 py-2 rounded-xl bg-purple-600 text-white text-xs font-semibold"
        >
          Retry
        </button>
      </div>
    );
  }

  const { model_metadata, als_metrics, popularity_baseline_metrics, comparison, curves, actual_vs_predicted_sample } = data;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-3">
          <Activity className="w-3.5 h-3.5" /> Quantitative Big Data Model Evaluation
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Model Performance & Benchmarking</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Comparative empirical evaluation of Apache Spark MLlib ALS against the Popularity Baseline.
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border-purple-500/30">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">ALS RMSE</span>
          <div className="text-2xl font-extrabold text-white mt-1">{als_metrics.rmse}</div>
          <span className="text-[11px] text-emerald-400 font-medium block mt-1">
            vs {popularity_baseline_metrics.rmse} Baseline ({(
              ((popularity_baseline_metrics.rmse - als_metrics.rmse) / popularity_baseline_metrics.rmse) * 100
            ).toFixed(1)}% better)
          </span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-blue-500/30">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">ALS MAE</span>
          <div className="text-2xl font-extrabold text-white mt-1">{als_metrics.mae}</div>
          <span className="text-[11px] text-emerald-400 font-medium block mt-1">
            vs {popularity_baseline_metrics.mae} Baseline
          </span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-amber-500/30">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Precision@10</span>
          <div className="text-2xl font-extrabold text-amber-300 mt-1">{(als_metrics.precision_at_10 * 100).toFixed(1)}%</div>
          <span className="text-[11px] text-gray-400 block mt-1">Threshold: ≥ 4.0 Stars</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border-cyan-500/30">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Recall@10</span>
          <div className="text-2xl font-extrabold text-cyan-300 mt-1">{(als_metrics.recall_at_10 * 100).toFixed(1)}%</div>
          <span className="text-[11px] text-gray-400 block mt-1">Relevant items retrieved</span>
        </div>
      </div>

      {/* Comparison Matrix Table */}
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-400" />
              Algorithm Comparison Matrix (ALS vs Popularity Baseline)
            </h2>
            <p className="text-xs text-gray-400">
              Evaluated on 19,633 held-out test ratings with ground-truth rating threshold of 4.0
            </p>
          </div>
          <span className="text-xs px-3 py-1 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
            {model_metadata.algorithm}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-xs uppercase text-gray-400 border-b border-gray-800">
                <th className="pb-3 font-semibold">Evaluation Metric</th>
                <th className="pb-3 font-semibold text-right">Spark MLlib ALS</th>
                <th className="pb-3 font-semibold text-right">Popularity Baseline</th>
                <th className="pb-3 font-semibold text-right">Relative Delta</th>
                <th className="pb-3 font-semibold text-center">Superior Model</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {comparison.map((row, idx) => (
                <tr key={idx} className="hover:bg-white/5 transition-colors">
                  <td className="py-3 font-medium text-gray-200">{row.metric}</td>
                  <td className="py-3 text-right font-bold text-purple-300">{row.als}</td>
                  <td className="py-3 text-right font-medium text-gray-400">{row.baseline}</td>
                  <td className="py-3 text-right font-semibold text-emerald-400">
                    +{row.improvement_percent}%
                  </td>
                  <td className="py-3 text-center">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      {row.better}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recharts Evaluation Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Actual vs Predicted Ratings Comparison */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Actual vs Predicted Ratings</h2>
              <p className="text-xs text-gray-400">Held-out test sample prediction fidelity</p>
            </div>
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={actual_vs_predicted_sample.slice(0, 30)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="movieId" stroke="#6B7280" tickLine={false} tickFormatter={(v) => `#${v}`} />
                <YAxis stroke="#6B7280" domain={[1, 5]} tickCount={5} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#374151", borderRadius: 12, color: "#fff" }}
                  formatter={(value, name) => [`${value} ★`, name === "actual" ? "Actual Rating" : "ALS Predicted"]}
                />
                <Legend />
                <Line type="monotone" dataKey="actual" stroke="#F59E0B" strokeWidth={2} dot={{ r: 3 }} name="Actual Rating" />
                <Line type="monotone" dataKey="predicted" stroke="#8B5CF6" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3 }} name="ALS Prediction" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Precision@K and Recall@K Curves */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Precision@K Ranking Curve</h2>
              <p className="text-xs text-gray-400">Precision benchmarked across K = [5, 10, 15, 20]</p>
            </div>
            <Activity className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={curves.precision_k}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="k" stroke="#6B7280" tickLine={false} tickFormatter={(v) => `K=${v}`} />
                <YAxis stroke="#6B7280" domain={[0.3, 0.8]} tickLine={false} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#374151", borderRadius: 12, color: "#fff" }}
                  formatter={(value) => [`${(value * 100).toFixed(1)}%`, "Precision"]}
                />
                <Legend />
                <Line type="monotone" dataKey="als" stroke="#8B5CF6" strokeWidth={2.5} name="ALS Collaborative" />
                <Line type="monotone" dataKey="baseline" stroke="#38BDF8" strokeWidth={2} strokeDasharray="3 3" name="Popularity Baseline" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Model Retraining Form Card */}
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-purple-400" />
              Hyperparameter Tuning & Retraining
            </h2>
            <p className="text-xs text-gray-400">
              Trigger distributed training on the Apache Spark engine with custom rank, iterations, and regularization.
            </p>
          </div>
        </div>

        <form onSubmit={handleRetrain} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Latent Factors (Rank):</label>
            <input
              type="number"
              min="2"
              max="50"
              value={rank}
              onChange={(e) => setRank(e.target.value)}
              className="w-full px-3.5 py-2 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Max Iterations:</label>
            <input
              type="number"
              min="1"
              max="30"
              value={maxIter}
              onChange={(e) => setMaxIter(e.target.value)}
              className="w-full px-3.5 py-2 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Reg Param (λ):</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max="1.0"
              value={regParam}
              onChange={(e) => setRegParam(e.target.value)}
              className="w-full px-3.5 py-2 bg-gray-900 border border-gray-700 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={retraining}
              className="w-full py-2 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm flex items-center justify-center gap-2 cursor-pointer transition-all disabled:opacity-50"
            >
              {retraining ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Retrain Model
            </button>
          </div>
        </form>

        {retrainMsg && (
          <div className="mt-4 p-3 rounded-xl bg-purple-500/10 border border-purple-500/30 text-xs text-purple-300 flex items-center gap-2">
            <Sparkles className="w-4 h-4 shrink-0" />
            <span>{retrainMsg}</span>
          </div>
        )}
      </div>
    </div>
  );
}
