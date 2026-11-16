import React, { useState, useEffect } from "react";
import { 
  LayoutDashboard, Film, Sparkles, Network, Activity, UserCheck, 
  Layers, Database, Menu, X, CheckCircle2, ShieldCheck 
} from "lucide-react";

import DashboardView from "./views/DashboardView";
import MovieExplorerView from "./views/MovieExplorerView";
import RecommendationsView from "./views/RecommendationsView";
import GraphAnalyticsView from "./views/GraphAnalyticsView";
import ModelPerformanceView from "./views/ModelPerformanceView";
import UserPreferenceView from "./views/UserPreferenceView";
import { fetchHealth } from "./api";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, desc: "Global Big Data KPIs" },
  { id: "explorer", label: "Movie Explorer", icon: Film, desc: "Catalog & Rating Inference" },
  { id: "recommendations", label: "Recommendations", icon: Sparkles, desc: "Spark MLlib ALS Engine" },
  { id: "graph", label: "Graph Analytics", icon: Network, desc: "Scala GraphX Bipartite Network" },
  { id: "model", label: "Model Performance", icon: Activity, desc: "RMSE & Precision Benchmarking" },
  { id: "users", label: "User Preferences", icon: UserCheck, desc: "Behavioral Taste Profiling" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [health, setHealth] = useState({ status: "checking", als_model_trained: false, graphx_data_available: false });

  useEffect(() => {
    async function checkBackend() {
      try {
        const res = await fetchHealth();
        setHealth(res);
      } catch (e) {
        setHealth({ status: "offline", als_model_trained: false, graphx_data_available: false });
      }
    }
    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#070B14] text-gray-100 flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-72 bg-[#0B1120]/95 backdrop-blur-xl border-r border-gray-800/80 p-5 flex flex-col justify-between
        transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:w-64 lg:w-72
        ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full"}
      `}>
        <div className="space-y-6">
          {/* Logo & Platform Name */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-400 p-0.5 shadow-lg shadow-purple-500/25 flex items-center justify-center">
                <div className="w-full h-full bg-[#0B1120] rounded-[14px] flex items-center justify-center">
                  <Film className="w-5 h-5 text-purple-400" />
                </div>
              </div>
              <div>
                <span className="font-extrabold text-lg text-white tracking-tight">Cine<span className="text-purple-400">Graph</span></span>
                <span className="text-[10px] text-gray-400 block font-mono">v1.0 • Big Data Analytics</span>
              </div>
            </div>

            <button 
              onClick={() => setMobileMenuOpen(false)}
              className="md:hidden p-1 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1.5">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`
                    w-full flex items-center gap-3.5 px-3.5 py-3 rounded-2xl text-left font-medium text-sm transition-all duration-200 cursor-pointer
                    ${isActive 
                      ? "bg-purple-600 text-white shadow-lg shadow-purple-600/30 font-semibold" 
                      : "text-gray-400 hover:text-white hover:bg-white/5"}
                  `}
                >
                  <Icon className={`w-5 h-5 ${isActive ? "text-white" : "text-gray-400"}`} />
                  <div>
                    <span className="block leading-none">{item.label}</span>
                    <span className={`text-[10px] mt-0.5 block ${isActive ? "text-purple-200" : "text-gray-500"}`}>
                      {item.desc}
                    </span>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Engine Status Card in Sidebar Footer */}
        <div className="p-3.5 rounded-2xl bg-gray-900/80 border border-gray-800 text-xs space-y-2">
          <div className="flex items-center justify-between text-gray-400 font-semibold text-[11px] uppercase tracking-wider">
            <span>Cluster Status</span>
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${health.status === "healthy" ? "bg-emerald-400 animate-pulse" : "bg-rose-500"}`}></span>
              <span className={health.status === "healthy" ? "text-emerald-400 font-bold" : "text-rose-400"}>
                {health.status === "healthy" ? "Online" : "Offline"}
              </span>
            </div>
          </div>
          <div className="flex items-center justify-between text-[11px] text-gray-400">
            <span>PySpark Engine:</span>
            <span className="text-purple-300 font-mono">v4.2.0 Active</span>
          </div>
          <div className="flex items-center justify-between text-[11px] text-gray-400">
            <span>Scala GraphX:</span>
            <span className="text-cyan-300 font-mono">Spark 3.5.9</span>
          </div>
          <div className="flex items-center justify-between text-[11px] text-gray-400">
            <span>Dataset:</span>
            <span className="text-gray-200 font-mono">MovieLens 100K</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <header className="sticky top-0 z-30 h-16 bg-[#070B14]/80 backdrop-blur-xl border-b border-gray-800/80 px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-2 rounded-xl text-gray-400 hover:text-white bg-gray-900"
            >
              <Menu className="w-5 h-5" />
            </button>
            <span className="text-sm font-semibold text-gray-300 hidden sm:inline">
              CineGraph – Distributed Movie Intelligence & Recommendation System
            </span>
          </div>

          {/* Engine Status Badges */}
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-300 border border-purple-500/20">
              <Database className="w-3.5 h-3.5" /> PySpark DataFrames
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
              <Network className="w-3.5 h-3.5" /> GraphX Scala
            </span>
          </div>
        </header>

        {/* View Content Body */}
        <main className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {activeTab === "dashboard" && <DashboardView />}
          {activeTab === "explorer" && <MovieExplorerView />}
          {activeTab === "recommendations" && <RecommendationsView />}
          {activeTab === "graph" && <GraphAnalyticsView />}
          {activeTab === "model" && <ModelPerformanceView />}
          {activeTab === "users" && <UserPreferenceView />}
        </main>
      </div>
    </div>
  );
}
