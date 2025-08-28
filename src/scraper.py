import requests
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)

def scrape_company_data(url):
    """Extract company data from website"""
    try:
        logger.info(f"Scraping: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic information
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # Extract main content
        body_text = soup.get_text(separator=' ', strip=True)[:2000]
        
        return {
            'url': url,
            'title': title_text,
            'description': description, 
            'content': body_text,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'url': url, 'success': False, 'error': str(e)}