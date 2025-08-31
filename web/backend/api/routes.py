"""API routes for the factsheet generator web interface"""

import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
import aiofiles

from .models import (
    GenerateRequest, GenerateResponse, TaskStatus, 
    FactsheetMetadata, FactsheetListResponse, FactsheetContent,
    BulkGenerateRequest, ErrorResponse
)

# Import existing components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../shared"))
from src.scraper import scrape_company_data
from src.synthesizer import create_factsheet
from src.logger import logger
from web.shared.utils import sanitize_filename

router = APIRouter(prefix="/api", tags=["factsheets"])

# In-memory task storage (in production, use Redis or similar)
tasks: Dict[str, TaskStatus] = {}

def get_factsheets_dir() -> Path:
    """Get the factsheets directory"""
    return Path("factsheets")

def get_factsheet_metadata(filepath: Path) -> FactsheetMetadata:
    """Extract metadata from factsheet file"""
    try:
        # Read content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Extract company name from filename as primary source
        filename_stem = filepath.stem  # e.g., "stripe" from "stripe.md"
        company_name = filename_stem.capitalize()  # e.g., "Stripe"
        
        # Try to extract URL from content
        url = "Unknown URL"
        for line in lines[:20]:
            if 'http' in line and ('website' in line.lower() or 'company' in line.lower()):
                import re
                # Try to match markdown link format [text](url) or just url
                url_match = re.search(r'\[(https?://[^\]]+)\]|\*\*Website:\*\*\s*\[(https?://[^\]]+)\]|https?://[^\s\)\]]+', line)
                if url_match:
                    # Get the first non-None group
                    url = next(group for group in url_match.groups() if group) if url_match.groups() and any(url_match.groups()) else url_match.group()
                    # Clean up markdown formatting
                    url = url.rstrip('/')
                    break
        
        stats = filepath.stat()
        
        return FactsheetMetadata(
            filename=filepath.name,
            company_name=company_name,
            url=url,
            word_count=len(content.split()),
            created_at=datetime.fromtimestamp(stats.st_mtime),
            file_size=stats.st_size,
            provider="openai"
        )
    except Exception as e:
        logger.error(f"Error extracting metadata from {filepath}: {e}")
        return FactsheetMetadata(
            filename=filepath.name,
            company_name="Unknown",
            url="Unknown",
            word_count=0,
            created_at=datetime.now(),
            file_size=filepath.stat().st_size,
            provider="unknown"
        )

async def generate_factsheet_task(task_id: str, url: str, model: Optional[str]):
    """Background task to generate factsheet"""
    try:
        tasks[task_id].status = "processing"
        tasks[task_id].progress = 10
        tasks[task_id].message = "Scraping company website..."
        
        # Step 1: Scrape company data
        company_data = scrape_company_data(url)
        
        if not company_data['success']:
            tasks[task_id].status = "failed"
            tasks[task_id].error = f"Failed to scrape data from {url}"
            return
        
        tasks[task_id].progress = 50
        tasks[task_id].message = "Generating factsheet with OpenAI..."
        
        # Step 2: Generate factsheet
        factsheet_content = create_factsheet(company_data, model=model)
        
        if not factsheet_content:
            tasks[task_id].status = "failed"
            tasks[task_id].error = "Failed to generate factsheet content"
            return
        
        tasks[task_id].progress = 80
        tasks[task_id].message = "Saving factsheet..."
        
        # Step 3: Save factsheet
        factsheets_dir = get_factsheets_dir()
        factsheets_dir.mkdir(exist_ok=True)
        
        page_title = company_data['homepage'].get('title', '')
        filename = sanitize_filename(page_title, url)
        
        # Extract clean company name from domain
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        domain = domain.replace('www.', '').replace('app.', '').replace('api.', '')
        company_name = domain.split('.')[0].capitalize()
        
        output_path = factsheets_dir / filename
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(factsheet_content)
        
        tasks[task_id].status = "completed"
        tasks[task_id].progress = 100
        tasks[task_id].message = "Factsheet generated successfully"
        tasks[task_id].result = {
            "filename": filename,
            "path": str(output_path),
            "word_count": len(factsheet_content.split()),
            "company_name": company_name
        }
        
        logger.info(f"Factsheet generated: {filename}")
        
    except Exception as e:
        tasks[task_id].status = "failed"
        tasks[task_id].error = str(e)
        logger.error(f"Error in factsheet generation task {task_id}: {e}")

@router.post("/generate", response_model=GenerateResponse)
async def generate_factsheet(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Generate a factsheet for a single company URL"""
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        progress=0,
        message="Task queued for processing"
    )
    
    # Start background task
    background_tasks.add_task(
        generate_factsheet_task,
        task_id,
        str(request.url),
        request.model
    )
    
    return GenerateResponse(
        task_id=task_id,
        message="Factsheet generation started"
    )

@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a factsheet generation task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

@router.get("/factsheets", response_model=FactsheetListResponse)
async def list_factsheets():
    """List all generated factsheets"""
    factsheets_dir = get_factsheets_dir()
    
    if not factsheets_dir.exists():
        return FactsheetListResponse(factsheets=[], total=0)
    
    factsheets = []
    for file_path in factsheets_dir.glob("*.md"):
        try:
            metadata = get_factsheet_metadata(file_path)
            factsheets.append(metadata)
        except Exception as e:
            logger.error(f"Error processing factsheet {file_path}: {e}")
    
    # Sort by creation date (newest first)
    factsheets.sort(key=lambda x: x.created_at, reverse=True)
    
    return FactsheetListResponse(
        factsheets=factsheets,
        total=len(factsheets)
    )

@router.get("/factsheets/{filename}", response_model=FactsheetContent)
async def get_factsheet(filename: str):
    """Get a specific factsheet by filename"""
    factsheets_dir = get_factsheets_dir()
    file_path = factsheets_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Factsheet not found")
    
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        metadata = get_factsheet_metadata(file_path)
        
        return FactsheetContent(
            metadata=metadata,
            content=content
        )
    except Exception as e:
        logger.error(f"Error reading factsheet {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error reading factsheet")

@router.delete("/factsheets/{filename}")
async def delete_factsheet(filename: str):
    """Delete a factsheet"""
    factsheets_dir = get_factsheets_dir()
    file_path = factsheets_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Factsheet not found")
    
    try:
        file_path.unlink()
        logger.info(f"Deleted factsheet: {filename}")
        return {"message": f"Factsheet {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting factsheet {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting factsheet")

@router.get("/factsheets/{filename}/download")
async def download_factsheet(filename: str):
    """Download a factsheet file"""
    factsheets_dir = get_factsheets_dir()
    file_path = factsheets_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Factsheet not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/markdown"
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}