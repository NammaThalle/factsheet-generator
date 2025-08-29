#!/bin/bash
# Start both backend and frontend services

echo "Starting Factsheet Generator Web Interface"
echo "============================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Please activate it first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# Install dependencies if not already installed
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Trap function to handle cleanup
cleanup() {
    echo ""
    echo "Stopping services..."
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
    fi
    echo "Services stopped"
    exit 0
}

# Set trap for SIGINT (Ctrl+C)
trap cleanup SIGINT

# Start backend in background
echo "Starting API backend (port 8000)..."
python scripts/start-backend.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting web frontend (port 8501)..."
echo "Open http://localhost:8501 in your browser"
echo ""
echo "Press Ctrl+C to stop both services"
python scripts/start-frontend.py

# If we get here, frontend exited normally
cleanup