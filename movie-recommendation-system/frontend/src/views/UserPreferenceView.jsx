import React, { useEffect, useState } from "react";
import { 
  User, Star, Heart, Activity, Users, Film, Search, Loader2, Sparkles, Award 
} from "lucide-react";
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell 
} from "recharts";
import { fetchUserPreferences, fetchSimilarUsers } from "../api";

const BAR_COLORS = ["#8B5CF6", "#38BDF8", "#34D399", "#FBBF24", "#F472B6", "#A78BFA"];

export default function UserPreferenceView() {
  const [userId, setUserId] = useState(1);
  const [profile, setProfile] = useState(null);
  const [similarUsers, setSimilarUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadUserProfile = async (idToLoad) => {
    try {
      setLoading(true);
      setError(null);
      const [profRes, simRes] = await Promise.all([
        fetchUserPreferences(idToLoad),
        fetchSimilarUsers(idToLoad, 5).catch(() => ({ similar_users: [] }))
      ]);
      setProfile(profRes);
      setSimilarUsers(simRes.similar_users || []);
    } catch (err) {
      setError(err.message || "User profile not found");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUserProfile(userId);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    loadUserProfile(userId);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 mb-3">
          <User className="w-3.5 h-3.5" /> Behavioral Profiling & Collaborative Clustering
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">User Preference & Taste Analysis</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Inspect individualized viewing patterns, favorite genre affinities, and peer users with matching taste vectors.
        </p>
      </div>

      {/* User Selection Search Bar */}
      <div className="glass-panel p-5 rounded-2xl">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="flex-1 w-full relative">
            <User className="w-4 h-4 absolute left-3.5 top-3 text-gray-400" />
            <input
              type="number"
              min="1"
              max="943"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter User ID (1 - 943)..."
              className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700/70 rounded-xl text-sm text-white focus:outline-none focus:border-purple-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-6 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm flex items-center justify-center gap-2 cursor-pointer transition-all"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            Inspect Profile
          </button>
        </form>
      </div>

      {error && (
        <div className="glass-panel p-5 rounded-2xl border-red-500/40 text-red-400 text-sm">
          {error}
        </div>
      )}

      {profile && (
        <div className="space-y-6">
          {/* User KPI Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-panel p-4 rounded-2xl">
              <span className="text-[11px] font-semibold text-gray-400 uppercase">Review Count</span>
              <div className="text-2xl font-bold text-white mt-1">{profile.total_ratings}</div>
              <span className="text-[11px] text-gray-500 block">Total movies reviewed</span>
            </div>

            <div className="glass-panel p-4 rounded-2xl">
              <span className="text-[11px] font-semibold text-gray-400 uppercase">Average Rating</span>
              <div className="text-2xl font-bold text-amber-300 mt-1 flex items-center gap-1">
                <Star className="w-5 h-5 fill-amber-300" /> {profile.average_rating}
              </div>
              <span className="text-[11px] text-gray-500 block">Across all watched titles</span>
            </div>

            <div className="glass-panel p-4 rounded-2xl">
              <span className="text-[11px] font-semibold text-gray-400 uppercase">Top Genre</span>
              <div className="text-xl font-bold text-purple-300 mt-1 truncate">
                {profile.favorite_genres[0]?.genre || "None"}
              </div>
              <span className="text-[11px] text-gray-500 block">
                {profile.favorite_genres[0]?.count || 0} reviews ({profile.favorite_genres[0]?.avg_rating || 0} ★)
              </span>
            </div>

            <div className="glass-panel p-4 rounded-2xl">
              <span className="text-[11px] font-semibold text-gray-400 uppercase">Genre Breadth</span>
              <div className="text-2xl font-bold text-cyan-300 mt-1">{profile.all_genres.length}</div>
              <span className="text-[11px] text-gray-500 block">Different genres rated</span>
            </div>
          </div>

          {/* Visual Breakdown: Genre Frequency Chart & Similar Users */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Genre Affinity Bar Chart */}
            <div className="glass-panel p-6 rounded-2xl lg:col-span-2">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-bold text-white">Genre Rating Frequency</h2>
                  <p className="text-xs text-gray-400">Total reviews submitted per genre by User {profile.userId}</p>
                </div>
                <Heart className="w-5 h-5 text-rose-400" />
              </div>

              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={profile.all_genres.slice(0, 10)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                    <XAxis dataKey="genre" stroke="#6B7280" tickLine={false} />
                    <YAxis stroke="#6B7280" tickLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "#0F172A", borderColor: "#374151", borderRadius: 12, color: "#fff" }}
                      formatter={(val, name, item) => [`${val} reviews (${item.payload.avg_rating} ★ avg)`, "Volume"]}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                      {profile.all_genres.slice(0, 10).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Similar Users Peer Cluster */}
            <div className="glass-panel p-6 rounded-2xl">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <Users className="w-5 h-5 text-cyan-400" />
                    Taste-Alike Users
                  </h2>
                  <p className="text-xs text-gray-400">Collaborative latent vector match</p>
                </div>
              </div>

              <div className="space-y-3">
                {similarUsers.map((peer, idx) => (
                  <div 
                    key={peer.userId}
                    onClick={() => { setUserId(peer.userId); loadUserProfile(peer.userId); }}
                    className="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 cursor-pointer flex items-center justify-between transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-300 font-bold text-xs">
                        #{idx + 1}
                      </span>
                      <div>
                        <span className="text-sm font-semibold text-white">User {peer.userId}</span>
                        <span className="text-[10px] text-gray-400 block">Match: {peer.similarity_score}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-extrabold text-cyan-400">
                        {peer.similarity_percentage}%
                      </span>
                      <span className="text-[10px] text-gray-500 block">Similarity</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* User Review History Table */}
          <div className="glass-panel p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Film className="w-5 h-5 text-purple-400" />
                  Recent Ratings by User {profile.userId}
                </h2>
                <p className="text-xs text-gray-400">Sorted from highest rated to lowest</p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="text-xs uppercase text-gray-400 border-b border-gray-800">
                    <th className="pb-3 font-semibold">Movie Title</th>
                    <th className="pb-3 font-semibold">Genres</th>
                    <th className="pb-3 font-semibold text-right">User Rating</th>
                    <th className="pb-3 font-semibold text-right">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {profile.recent_ratings.map((r, idx) => (
                    <tr key={idx} className="hover:bg-white/5 transition-colors">
                      <td className="py-2.5 font-medium text-gray-200">{r.title}</td>
                      <td className="py-2.5 text-xs text-gray-400">{r.genres}</td>
                      <td className="py-2.5 text-right">
                        <span className="inline-flex items-center gap-1 font-bold text-amber-300 text-xs">
                          <Star className="w-3.5 h-3.5 fill-amber-300" /> {r.rating}
                        </span>
                      </td>
                      <td className="py-2.5 text-right text-xs text-gray-500 font-mono">
                        {r.datetime || "N/A"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
