@echo off
echo Starting Backend API (Port 8000)...
start "Backend API" cmd /k "python -m uvicorn src.api.main:app --reload --port 8000"

echo Starting Frontend Dashboard (Port 3000)...
cd src\web
start "Frontend Dashboard" cmd /k "npm run dev"
cd ..\..

echo Full system running.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Close the popup windows to stop the servers.
pause
