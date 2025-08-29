"""Shared utilities for the web interface"""

import requests
from typing import Dict, List, Optional, Any
import time
import streamlit as st

class APIClient:
    """Client for communicating with the FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def generate_factsheet(self, url: str, provider: str = "gemini", model: Optional[str] = None) -> Dict[str, Any]:
        """Start factsheet generation"""
        data = {"url": url, "provider": provider}
        if model:
            data["model"] = model
        
        response = self.session.post(f"{self.base_url}/api/generate", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        response = self.session.get(f"{self.base_url}/api/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def list_factsheets(self) -> Dict[str, Any]:
        """List all factsheets"""
        response = self.session.get(f"{self.base_url}/api/factsheets")
        response.raise_for_status()
        return response.json()
    
    def get_factsheet(self, filename: str) -> Dict[str, Any]:
        """Get specific factsheet content"""
        response = self.session.get(f"{self.base_url}/api/factsheets/{filename}")
        response.raise_for_status()
        return response.json()
    
    def delete_factsheet(self, filename: str) -> Dict[str, Any]:
        """Delete a factsheet"""
        response = self.session.delete(f"{self.base_url}/api/factsheets/{filename}")
        response.raise_for_status()
        return response.json()
    
    def download_factsheet(self, filename: str) -> bytes:
        """Download factsheet file"""
        response = self.session.get(f"{self.base_url}/api/factsheets/{filename}/download")
        response.raise_for_status()
        return response.content
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except:
            return False

def wait_for_task_completion(api_client: APIClient, task_id: str, progress_bar=None, status_text=None):
    """Wait for task completion with progress updates"""
    while True:
        try:
            status = api_client.get_task_status(task_id)
            
            if progress_bar:
                progress_bar.progress(status['progress'] / 100)
            
            if status_text:
                status_text.text(status['message'])
            
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(status.get('error', 'Task failed'))
            
            time.sleep(1)  # Poll every second
            
        except Exception as e:
            raise Exception(f"Error checking task status: {e}")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def get_company_name_from_url(url: str) -> str:
    """Extract company name from URL"""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        # Remove www. and common prefixes
        domain = domain.replace('www.', '').replace('app.', '').replace('api.', '')
        # Take the main domain name
        name = domain.split('.')[0]
        return name.replace('-', ' ').replace('_', ' ').title()
    except:
        return "Unknown Company"