#!/usr/bin/env python3
"""Start the FastAPI backend server"""

import os
import sys
import uvicorn

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

from web.backend.app import app

if __name__ == "__main__":
    print("Starting Factsheet Generator API Backend...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/health")
    print("---")
    
    uvicorn.run(
        "web.backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )