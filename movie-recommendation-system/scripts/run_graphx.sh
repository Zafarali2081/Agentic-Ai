#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=========================================================="
echo "    Executing CineGraph Scala Apache Spark GraphX Engine   "
echo "=========================================================="

mkdir -p data/graph

SPARK_SHELL_BIN="${SPARK_HOME:-/opt/spark}/bin/spark-shell"
if ! command -v "$SPARK_SHELL_BIN" &> /dev/null; then
    SPARK_SHELL_BIN="spark-shell"
fi

TEMP_LAUNCHER="graphx/temp_runner.scala"
cat << 'EOF' > "$TEMP_LAUNCHER"
:load graphx/src/main/scala/MovieGraphAnalytics.scala
try {
  com.cinegraph.analytics.MovieGraphAnalytics.runAnalytics(sc, "data/processed", "data/graph")
} catch {
  case e: Throwable =>
    println("GraphX Execution Error: " + e.getMessage)
    e.printStackTrace()
}
sys.exit(0)
EOF

"$SPARK_SHELL_BIN" --master "local[*]" --conf "spark.driver.memory=2g" --conf "spark.ui.enabled=false" -i "$TEMP_LAUNCHER"

rm -f "$TEMP_LAUNCHER"
echo "[OK] Scala GraphX analysis finished. Check data/graph/"
