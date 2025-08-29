"""
Web Scraping Module

Extracts content from company websites including homepage and about pages
for factsheet generation.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from logger import logger

def find_about_page(base_url, soup):
    """Try to find the About page URL"""
    about_patterns = ['about', 'about-us', 'company', 'our-story']
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').lower()
        link_text = link.get_text().lower().strip()
        
        for pattern in about_patterns:
            if pattern in href or pattern in link_text:
                return urljoin(base_url, link.get('href'))
    return None

def scrape_page(url):
    """Scrape a single page and extract content"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract key information
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()
        
        # Extract main text content
        body_text = soup.get_text(separator=' ', strip=True)
        
        return {
            'title': title_text,
            'description': description,
            'content': body_text[:3000],  # Limit content length
            'success': True
        }
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'success': False, 'error': str(e)}

def scrape_company_data(url):
    """Extract comprehensive company data from website"""
    logger.info(f"Scraping company: {url}")
    
    # Scrape homepage
    homepage_data = scrape_page(url)
    if not homepage_data['success']:
        return {'url': url, 'success': False, 'error': homepage_data['error']}
    
    result = {
        'url': url,
        'homepage': homepage_data,
        'about': {},
        'success': True
    }
    
    # Try to find and scrape About page
    try:
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        about_url = find_about_page(url, soup)
        
        if about_url:
            logger.info(f"Found about page: {about_url}")
            time.sleep(1)  # Be respectful with requests
            about_data = scrape_page(about_url)
            if about_data['success']:
                result['about'] = about_data
        
    except Exception as e:
        logger.warning(f"Could not scrape about page: {str(e)}")
    
    return result