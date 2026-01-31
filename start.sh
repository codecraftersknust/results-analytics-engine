#!/bin/bash

# Function to kill processes on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "Starting Backend API (Port 8000)..."
uvicorn src.api.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend Dashboard (Port 3000)..."
cd src/web && npm run dev &
FRONTEND_PID=$!

echo "Full system running."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop."

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
