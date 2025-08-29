"""API models for the web interface"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

class GenerateRequest(BaseModel):
    """Request model for factsheet generation"""
    url: HttpUrl = Field(..., description="Company website URL to analyze")
    provider: str = Field(default="gemini", description="AI provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")

class GenerateResponse(BaseModel):
    """Response model for factsheet generation"""
    task_id: str = Field(..., description="Task ID for tracking generation progress")
    message: str = Field(..., description="Response message")

class TaskStatus(BaseModel):
    """Task status response"""
    task_id: str
    status: str = Field(..., description="pending, processing, completed, failed")
    progress: int = Field(0, description="Progress percentage (0-100)")
    message: str = Field("", description="Current status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Result data if completed")
    error: Optional[str] = Field(None, description="Error message if failed")

class FactsheetMetadata(BaseModel):
    """Factsheet metadata"""
    filename: str
    company_name: str
    url: str
    word_count: int
    created_at: datetime
    file_size: int
    provider: str

class FactsheetListResponse(BaseModel):
    """Response for listing factsheets"""
    factsheets: List[FactsheetMetadata]
    total: int
    
class FactsheetContent(BaseModel):
    """Full factsheet content"""
    metadata: FactsheetMetadata
    content: str

class BulkGenerateRequest(BaseModel):
    """Request for bulk factsheet generation"""
    urls: List[HttpUrl] = Field(..., description="List of company URLs")
    provider: str = Field(default="gemini", description="AI provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    status_code: int