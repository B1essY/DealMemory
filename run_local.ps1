Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Starting DealMemory Locally (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Launching Backend Server on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "[2/2] Launching Frontend Server on http://127.0.0.1:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`n====================================================" -ForegroundColor Green
Write-Host "DealMemory is now live!" -ForegroundColor Green
Write-Host "Web Application: http://localhost:5173" -ForegroundColor White
Write-Host "API Swagger Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "System Health:   http://localhost:8000/health/detailed" -ForegroundColor White
Write-Host "====================================================" -ForegroundColor Green
