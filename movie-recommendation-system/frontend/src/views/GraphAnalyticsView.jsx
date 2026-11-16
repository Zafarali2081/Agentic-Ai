import React, { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";
import { 
  Network, Share2, Layers, Award, TrendingUp, Info, Loader2, Sparkles, RefreshCw, ZoomIn, ZoomOut 
} from "lucide-react";
import { fetchGraphAnalytics } from "../api";

export default function GraphAnalyticsView() {
  const cyContainerRef = useRef(null);
  const cyRef = useRef(null);

  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await fetchGraphAnalytics();
        setGraphData(data);
      } catch (err) {
        setError(err.message || "Failed to load GraphX analytics");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Initialize Cytoscape.js when subgraph data is ready
  useEffect(() => {
    if (!graphData || !graphData.subgraph || !cyContainerRef.current) return;

    const elements = [
      ...graphData.subgraph.nodes.map((n) => ({
        data: {
          id: n.id,
          label: n.label,
          type: n.type,
          genres: n.genres,
          rank: n.rank || 1.0,
        },
      })),
      ...graphData.subgraph.edges.map((e, idx) => ({
        data: {
          id: `e_${idx}`,
          source: e.source,
          target: e.target,
          rating: e.rating,
        },
      })),
    ];

    try {
      cyRef.current = cytoscape({
        container: cyContainerRef.current,
        elements,
        style: [
          {
            selector: "node",
            style: {
              label: "data(label)",
              color: "#E2E8F0",
              "font-size": "10px",
              "text-valign": "bottom",
              "text-margin-y": "5px",
              "background-color": (ele) => (ele.data("type") === "user" ? "#38BDF8" : "#A78BFA"),
              width: (ele) => (ele.data("type") === "user" ? 22 : Math.min(42, Math.max(24, ele.data("rank") * 12))),
              height: (ele) => (ele.data("type") === "user" ? 22 : Math.min(42, Math.max(24, ele.data("rank") * 12))),
              "border-width": 2,
              "border-color": (ele) => (ele.data("type") === "user" ? "#0284C7" : "#7C3AED"),
            },
          },
          {
            selector: "node:selected",
            style: {
              "border-width": 4,
              "border-color": "#F59E0B",
              "background-color": "#FBBF24",
              color: "#FBBF24",
              "font-weight": "bold",
            },
          },
          {
            selector: "edge",
            style: {
              width: 1.2,
              "line-color": "#4B5563",
              opacity: 0.45,
              "curve-style": "bezier",
            },
          },
        ],
        layout: {
          name: "cose",
          idealEdgeLength: 60,
          nodeOverlap: 20,
          refresh: 20,
          fit: true,
          padding: 30,
          randomize: false,
          componentSpacing: 100,
          nodeRepulsion: 400000,
          edgeElasticity: 100,
          nestingFactor: 5,
        },
      });

      cyRef.current.on("tap", "node", (evt) => {
        setSelectedNode(evt.target.data());
      });

      cyRef.current.on("tap", (evt) => {
        if (evt.target === cyRef.current) {
          setSelectedNode(null);
        }
      });
    } catch (e) {
      console.error("Cytoscape init error:", e);
    }

    return () => {
      if (cyRef.current) cyRef.current.destroy();
    };
  }, [graphData]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3 text-purple-400">
        <Loader2 className="w-10 h-10 animate-spin" />
        <p className="text-gray-400 font-medium">Loading Apache Spark GraphX output...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel p-6 rounded-2xl border-red-500/30 text-red-400">
        <p className="font-semibold">GraphX Analytics unavailable:</p>
        <p className="text-sm text-gray-400 mt-1">{error}</p>
        <p className="text-xs text-gray-500 mt-3">
          To run GraphX: Execute <code className="bg-black/50 px-2 py-1 rounded">powershell scripts/run_graphx.ps1</code>
        </p>
      </div>
    );
  }

  const { summary, degrees, pagerank_nodes, communities } = graphData;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-3">
          <Share2 className="w-3.5 h-3.5" /> Scala GraphX Bipartite Network Engine
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Graph Analytics & Network Centrality</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Structural analysis of user-movie interactions via Degree Centrality, PageRank, Connected Components, and Community Detection.
        </p>
      </div>

      {/* Graph Metrics KPI Summary */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="glass-panel p-4 rounded-2xl">
          <span className="text-[11px] font-semibold text-gray-400 uppercase">Total Vertices</span>
          <div className="text-xl font-bold text-white mt-1">{summary.total_vertices.toLocaleString()}</div>
        </div>
        <div className="glass-panel p-4 rounded-2xl">
          <span className="text-[11px] font-semibold text-gray-400 uppercase">User Nodes</span>
          <div className="text-xl font-bold text-cyan-400 mt-1">{summary.total_users.toLocaleString()}</div>
        </div>
        <div className="glass-panel p-4 rounded-2xl">
          <span className="text-[11px] font-semibold text-gray-400 uppercase">Movie Nodes</span>
          <div className="text-xl font-bold text-purple-400 mt-1">{summary.total_movies.toLocaleString()}</div>
        </div>
        <div className="glass-panel p-4 rounded-2xl">
          <span className="text-[11px] font-semibold text-gray-400 uppercase">Total Edges</span>
          <div className="text-xl font-bold text-emerald-400 mt-1">{summary.total_edges.toLocaleString()}</div>
        </div>
        <div className="glass-panel p-4 rounded-2xl">
          <span className="text-[11px] font-semibold text-gray-400 uppercase">Connected Comp.</span>
          <div className="text-xl font-bold text-amber-400 mt-1">{summary.connected_components}</div>
        </div>
        <div className="glass-panel p-4 rounded-2xl">
          <span className="text-[11px] font-semibold text-gray-400 uppercase">Average Degree</span>
          <div className="text-xl font-bold text-blue-400 mt-1">{summary.average_degree}</div>
        </div>
      </div>

      {/* Interactive Cytoscape.js Canvas Card */}
      <div className="glass-panel p-6 rounded-2xl relative">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Network className="w-5 h-5 text-purple-400" />
              Interactive Bipartite Subgraph Canvas
            </h2>
            <p className="text-xs text-gray-400">
              Sample bipartite subgraph rendered with Cytoscape.js. Blue = Users, Purple = Movies (node size scaled by PageRank).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 1.25)}
              className="p-1.5 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 0.8)}
              className="p-1.5 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => cyRef.current && cyRef.current.fit()}
              className="p-1.5 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700"
              title="Fit View"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Graph Canvas Container */}
        <div 
          ref={cyContainerRef} 
          className="w-full h-96 rounded-xl bg-gray-950/80 border border-gray-800/80"
        />

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute bottom-10 right-10 max-w-xs p-4 rounded-2xl glass-panel-glow border-purple-500/40 text-xs animate-fadeIn">
            <div className="font-bold text-white text-sm mb-1">{selectedNode.label}</div>
            <div className="text-purple-300 uppercase tracking-wider text-[10px] font-semibold mb-2">
              Type: {selectedNode.type}
            </div>
            {selectedNode.genres && (
              <p className="text-gray-400 mb-1">Genres: <span className="text-gray-200">{selectedNode.genres}</span></p>
            )}
            <p className="text-gray-400">PageRank: <span className="text-cyan-300 font-mono font-bold">{selectedNode.rank}</span></p>
          </div>
        )}
      </div>

      {/* Two Column Section: PageRank vs Average Rating & Communities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PageRank Influence Table */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
                PageRank Structural Influence
              </h2>
              <p className="text-xs text-gray-400">
                Measures graph topology influence (connectivity to active reviewers) vs rating quality.
              </p>
            </div>
          </div>
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-left text-sm">
              <thead className="sticky top-0 bg-[#0F172A] border-b border-gray-800 text-xs text-gray-400 uppercase">
                <tr>
                  <th className="pb-2.5">Title</th>
                  <th className="pb-2.5 text-right">PageRank</th>
                  <th className="pb-2.5 text-right">Avg Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {pagerank_nodes.slice(0, 15).map((node, i) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="py-2.5 text-xs text-gray-200 max-w-[200px] truncate">{node.title}</td>
                    <td className="py-2.5 text-right font-mono font-semibold text-cyan-400 text-xs">
                      {node.pagerank.toFixed(4)}
                    </td>
                    <td className="py-2.5 text-right font-semibold text-amber-300 text-xs">
                      {node.avg_rating} ★
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* User Communities Section */}
        <div className="glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-purple-400" />
                Detected User Communities (LPA)
              </h2>
              <p className="text-xs text-gray-400">
                Clusters generated via GraphX Label Propagation with common shared movies.
              </p>
            </div>
          </div>
          <div className="space-y-4 max-h-96 overflow-y-auto pr-1">
            {communities.slice(0, 5).map((comm) => (
              <div key={comm.communityId} className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-sm text-purple-300">Community #{comm.communityId}</span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 font-mono">
                    {comm.userCount} Members
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  <span className="text-gray-500 font-medium">Consensus Titles:</span>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {comm.topMovies.map((m) => (
                      <span key={m.movieId} className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 text-[11px]">
                        {m.title} ({m.votes} votes)
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
