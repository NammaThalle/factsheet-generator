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

# Install web dependencies if not already installed
echo "Installing web dependencies..."
pip install -r requirements-web.txt -q

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

# Clean up background process when frontend stops
echo "Stopping services..."
kill $BACKEND_PID 2>/dev/null
echo "Services stopped"