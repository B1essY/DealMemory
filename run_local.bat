@echo off
echo ====================================================
echo Starting DealMemory Locally (Backend + Frontend)
echo ====================================================

echo [1/2] Launching Backend Server on http://127.0.0.1:8000 ...
start "DealMemory Backend (FastAPI)" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Launching Frontend Server on http://127.0.0.1:5173 ...
start "DealMemory Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================================
echo DealMemory is now live!
echo Web Application: http://localhost:5173
echo API Swagger Docs: http://localhost:8000/docs
echo System Health:   http://localhost:8000/health/detailed
echo ====================================================
