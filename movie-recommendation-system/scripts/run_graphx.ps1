# PowerShell script to compile and execute the Scala GraphX application
$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR
Set-Location $PROJECT_ROOT

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    Executing CineGraph Scala Apache Spark GraphX Engine   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Ensure output directory exists
$DATA_GRAPH_DIR = Join-Path $PROJECT_ROOT "data\graph"
if (-not (Test-Path $DATA_GRAPH_DIR)) {
    New-Item -ItemType Directory -Force -Path $DATA_GRAPH_DIR | Out-Null
}

$CLASSES_DIR = Join-Path $PROJECT_ROOT "graphx\classes"
if (-not (Test-Path $CLASSES_DIR)) {
    New-Item -ItemType Directory -Force -Path $CLASSES_DIR | Out-Null
}

# Locate Java and Spark
$JAVA_EXE = "C:\Program Files\Java\jre1.8.0_491\bin\java.exe"
$SPARK_JARS = "C:\spark\spark-3.5.9-bin-hadoop3\jars\*"

if (-not (Test-Path $JAVA_EXE)) {
    $JAVA_EXE = "java"
}

Write-Host "[*] Compiling MovieGraphAnalytics.scala using Scala Compiler..." -ForegroundColor Yellow
& $JAVA_EXE "-Dscala.usejavacp=true" -cp $SPARK_JARS scala.tools.nsc.Main -usejavacp -d "graphx\classes" "graphx\src\main\scala\MovieGraphAnalytics.scala"

Write-Host "[*] Running GraphX analytics on bipartite graph..." -ForegroundColor Green
& $JAVA_EXE "-Dspark.master=local[*]" "-Dspark.driver.host=127.0.0.1" "-Dspark.driver.bindAddress=127.0.0.1" `
    -cp "graphx\classes;$SPARK_JARS" com.cinegraph.analytics.MovieGraphAnalytics "data/processed" "data/graph"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[OK] Scala GraphX analysis finished. Check data/graph/" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
