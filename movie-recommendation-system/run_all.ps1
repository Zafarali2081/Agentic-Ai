# CineGraph All-in-One Launcher
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   Starting CineGraph (FastAPI + PySpark + React Dashboard)           " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Unified Server (UI + API): http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Interactive Swagger Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

py -3 backend/main.py
