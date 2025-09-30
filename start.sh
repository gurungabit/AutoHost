#!/bin/bash

# AutoHost Quick Start Script

echo "Starting AutoHost - 3270 Terminal Automation Builder"
echo "===================================================="

# Check if backend is setup
if [ ! -d "backend/.venv" ]; then
    echo "Setting up backend..."
    cd backend
    uv sync
    cd ..
fi

# Check if frontend is setup
if [ ! -d "frontend/node_modules" ]; then
    echo "Setting up frontend..."
    cd frontend
    npm install
    cd ..
fi

# Create necessary directories
mkdir -p scripts logs

# Start backend in background
echo "Starting backend server..."
cd backend
uv run python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "===================================================="
echo "AutoHost is running!"
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "===================================================="

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
