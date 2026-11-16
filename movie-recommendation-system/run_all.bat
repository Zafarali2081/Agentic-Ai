@echo off
title CineGraph - Movie Intelligence & Recommendation System
echo ======================================================================
echo    Starting CineGraph (FastAPI + PySpark + React Dashboard)
echo ======================================================================
echo Backend and UI will be available at: http://127.0.0.1:8000
echo Interactive API Swagger docs at:     http://127.0.0.1:8000/docs
echo ======================================================================

cd /d "%~dp0"
py -3 backend/main.py
pause
