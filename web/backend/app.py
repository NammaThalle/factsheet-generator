"""
FastAPI Backend Application

REST API backend for the factsheet generator web interface.
Provides endpoints for factsheet generation, management, and file operations.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from .api.routes import router
from src.logger import logger

# Create FastAPI app
app = FastAPI(
    title="Factsheet Generator API",
    description="AI-powered company factsheet generation API for sales teams",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Serve static files if needed
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("Starting Factsheet Generator API server")
    
    # Ensure factsheets directory exists
    factsheets_dir = Path("factsheets")
    factsheets_dir.mkdir(exist_ok=True)
    
    logger.success("API server startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("Shutting down Factsheet Generator API server")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Factsheet Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FastAPI server in development mode")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )