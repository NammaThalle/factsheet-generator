#!/usr/bin/env python3
"""Start the Streamlit frontend"""

import os
import subprocess
import sys

# Path to the Streamlit app
frontend_app = os.path.join(os.path.dirname(__file__), "../web/frontend/app.py")

if __name__ == "__main__":
    print("Starting Factsheet Generator Web Interface...")
    print("Web App: http://localhost:8501")
    print("Make sure the backend API is running on port 8000")
    print("---")
    
    # Start Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", frontend_app,
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ])