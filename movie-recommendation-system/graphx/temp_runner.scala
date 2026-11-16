:load C:/Users/zafar/OneDrive/Desktop/Agentic AI/movie-recommendation-system/graphx/src/main/scala/MovieGraphAnalytics.scala
try {
  com.cinegraph.analytics.MovieGraphAnalytics.runAnalytics(sc, "C:/Users/zafar/OneDrive/Desktop/Agentic AI/movie-recommendation-system/data/processed", "C:/Users/zafar/OneDrive/Desktop/Agentic AI/movie-recommendation-system/data/graph")
} catch {
  case e: Throwable =>
    println("GraphX Execution Error: " + e.getMessage)
    e.printStackTrace()
}
sys.exit(0)
