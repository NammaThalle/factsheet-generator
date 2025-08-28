"""Data models for the factsheet generator"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
import re

class PageData(BaseModel):
    """Model for scraped page data"""
    title: str = ""
    description: str = ""
    content: str = ""
    success: bool = False

class CompanyData(BaseModel):
    """Model for complete company data"""
    url: str
    homepage: PageData = Field(default_factory=PageData)
    about: PageData = Field(default_factory=PageData) 
    success: bool = False
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class FactsheetOutput(BaseModel):
    """Model for factsheet output with cleaning"""
    content: str
    filename: str
    word_count: int = 0
    
    @validator('filename', pre=True)
    def clean_filename(cls, v):
        if not v:
            return "factsheet.md"
        
        # Clean filename
        clean_name = str(v).lower()
        clean_name = re.sub(r'[^\w\s-]', '', clean_name)
        clean_name = re.sub(r'[-\s]+', '-', clean_name)
        clean_name = clean_name.strip('-')
        
        if not clean_name.endswith('.md'):
            clean_name += '.md'
            
        return clean_name or "factsheet.md"
    
    @validator('word_count', always=True)
    def calculate_word_count(cls, v, values):
        content = values.get('content', '')
        return len(str(content).split()) if content else 0