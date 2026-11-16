import React, { useEffect, useState } from "react";
import { 
  Users, Film, Star, BarChart3, TrendingUp, Layers, Flame, Award, Loader2, Sparkles 
} from "lucide-react";
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  AreaChart, Area, CartesianGrid, PieChart, Pie, Cell 
} from "recharts";
import { fetchDashboardStats, fetchGenreAnalytics } from "../api";

const GENRE_COLORS = [
  "#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EC4899", 
  "#6366F1", "#14B8A6", "#F97316", "#84CC16", "#06B6D4"
];

export default function DashboardView() {
  const [data, setData] = useState(null);
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [dashRes, genreRes] = await Promise.all([
          fetchDashboardStats(),
          fetchGenreAnalytics()
        ]);
        setData(dashRes);
        setGenres(genreRes.genres || []);
      } catch (err) {
        setError(err.message || "Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3 text-purple-400">
        <Loader2 className="w-10 h-10 animate-spin" />
        <p className="text-gray-400 font-medium">Aggregating distributed Spark metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel p-6 rounded-2xl border-red-500/30 text-red-400">
        <p className="font-semibold">Unable to load dashboard:</p>
        <p className="text-sm text-gray-400 mt-1">{error}</p>
      </div>
    );
  }

  const { stats, rating_distribution, monthly_activity, top_popular_movies } = data;

  const statCards = [
    { title: "Total Users", value: stats.total_users.toLocaleString(), icon: Users, color: "text-blue-400", sub: "Active reviewers" },
    { title: "Total Movies", value: stats.total_movies.toLocaleString(), icon: Film, color: "text-purple-400", sub: "Catalog titles" },
    { title: "Total Ratings", value: stats.total_ratings.toLocaleString(), icon: BarChart3, color: "text-emerald-400", sub: "Processed reviews" },
    { title: "Average Rating", value: `${stats.average_rating} / 5.0`, icon: Star, color: "text-amber-400", sub: "Global consensus" },
    { title: "Distinct Genres", value: stats.total_genres, icon: Layers, color: "text-cyan-400", sub: "Taxonomy categories" },
    { title: "Most Popular Title", value: stats.most_popular_movie, icon: Flame, color: "text-rose-400", sub: `${stats.most_popular_count} ratings` },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20 mb-3">
          <Sparkles className="w-3.5 h-3.5" /> Distributed PySpark Analytics Pipeline
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Platform Intelligence Overview</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Real-time aggregated statistics processed through Apache Spark DataFrames and Spark SQL.
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="glass-panel p-5 rounded-2xl hover:border-purple-500/30 transition-all duration-300">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{card.title}</span>
                <div className={`p-2 rounded-xl bg-white/5 ${card.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div className="text-2xl font-bold text-white truncate">{card.value}</div>
              <p className="text-xs text-gray-500 mt-1">{card.sub}</p>
            </div>
          );
        })}
      </div>

      {/* Primary Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ratings Distribution Bar Chart */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Ratings Distribution</h2>
              <p className="text-xs text-gray-400">Frequency breakdown across 1.0 to 5.0 stars</p>
            </div>
            <Star className="w-5 h-5 text-amber-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rating_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="rating" stroke="#6B7280" tickLine={false} tickFormatter={(v) => `${v} ★`} />
                <YAxis stroke="#6B7280" tickLine={false} tickFormatter={(v) => `${v / 1000}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#374151", borderRadius: 12, color: "#fff" }}
                  formatter={(value, name, item) => [`${value.toLocaleString()} reviews (${item.payload.percentage}%)`, "Volume"]}
                />
                <Bar dataKey="count" fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8B5CF6" />
                    <stop offset="100%" stopColor="#3B82F6" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Activity Area Chart */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Temporal Review Activity</h2>
              <p className="text-xs text-gray-400">Monthly rating submissions over time</p>
            </div>
            <TrendingUp className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly_activity}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="month_year" stroke="#6B7280" tickLine={false} />
                <YAxis stroke="#6B7280" tickLine={false} tickFormatter={(v) => `${v / 1000}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#374151", borderRadius: 12, color: "#fff" }}
                  formatter={(value) => [`${value.toLocaleString()} ratings`, "Activity"]}
                />
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#38BDF8" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#38BDF8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area type="monotone" dataKey="rating_count" stroke="#38BDF8" strokeWidth={2} fill="url(#areaGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Secondary Section: Popular Genres & Top 10 Movies */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Genres List */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Genre Popularity</h2>
            <Layers className="w-5 h-5 text-purple-400" />
          </div>
          <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
            {genres.slice(0, 10).map((g, idx) => (
              <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: GENRE_COLORS[idx % GENRE_COLORS.length] }}></span>
                  <span className="font-medium text-sm text-gray-200">{g.genre}</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-semibold text-purple-300">{g.total_ratings.toLocaleString()} reviews</span>
                  <span className="text-[11px] text-gray-400 block">{g.avg_rating} ★ avg</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top 10 Popular Movies Table */}
        <div className="glass-panel p-6 rounded-2xl lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Top 10 Most Popular Movies</h2>
              <p className="text-xs text-gray-400">Ranked by total review volume on MovieLens</p>
            </div>
            <Award className="w-5 h-5 text-amber-400" />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-xs uppercase text-gray-400 border-b border-gray-800">
                  <th className="pb-3 font-semibold">#</th>
                  <th className="pb-3 font-semibold">Title</th>
                  <th className="pb-3 font-semibold">Genres</th>
                  <th className="pb-3 font-semibold text-right">Reviews</th>
                  <th className="pb-3 font-semibold text-right">Avg Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {top_popular_movies.map((m, idx) => (
                  <tr key={m.movieId} className="hover:bg-white/5 transition-colors">
                    <td className="py-2.5 font-bold text-purple-400 text-xs">{idx + 1}</td>
                    <td className="py-2.5 font-medium text-gray-100 max-w-[200px] truncate">{m.title}</td>
                    <td className="py-2.5 text-xs text-gray-400 max-w-[150px] truncate">{m.genres}</td>
                    <td className="py-2.5 text-right font-semibold text-blue-400">{m.rating_count}</td>
                    <td className="py-2.5 text-right">
                      <span className="inline-flex items-center gap-1 font-semibold text-amber-300 text-xs">
                        <Star className="w-3 h-3 fill-amber-300" /> {m.avg_rating}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
