"""
Deep Web Intelligence Module

Advanced intelligence gathering from multiple sources beyond basic web scraping.
Provides comprehensive business intelligence for sales teams.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, quote
import re

from logger import logger

class DeepWebIntelligence:
    """Advanced intelligence gathering from multiple web sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def gather_intelligence(self, company_data) -> Dict[str, Any]:
        """Gather comprehensive intelligence from multiple sources"""
        company_name = self._extract_company_name(company_data)
        url = company_data.get('url') if isinstance(company_data, dict) else company_data.url
        domain = self._extract_domain(url)
        
        intelligence = {
            'company_name': company_name,
            'domain': domain,
            'linkedin_data': self._get_linkedin_intelligence(company_name, domain),
            'news_sentiment': self._analyze_news_sentiment(company_name),
            'funding_data': self._get_funding_intelligence(company_name, domain),
            'tech_stack': self._detect_technology_stack(url),
            'social_presence': self._analyze_social_presence(company_name, domain),
            'competitive_landscape': self._identify_competitors(company_name, company_data),
            'growth_indicators': self._detect_growth_signals(company_name, domain),
            'contact_intelligence': self._find_key_contacts(company_name, domain)
        }
        
        return intelligence
    
    def _extract_company_name(self, company_data) -> str:
        """Extract clean company name from various sources"""
        # Handle both dict and CompanyData object
        if isinstance(company_data, dict):
            title = company_data.get('homepage', {}).get('title', '').lower()
        else:
            title = company_data.homepage.title.lower()
        
        # Remove common suffixes
        suffixes = ['inc', 'llc', 'corp', 'corporation', 'company', 'co', 'ltd', 'limited']
        
        # Try to extract from title
        if '|' in title:
            company_part = title.split('|')[0].strip()
        elif '-' in title:
            company_part = title.split('-')[0].strip()
        else:
            company_part = title.strip()
        
        # Clean up
        for suffix in suffixes:
            company_part = re.sub(rf'\b{suffix}\b', '', company_part, flags=re.IGNORECASE).strip()
        
        return company_part.title()
    
    def _extract_domain(self, url: str) -> str:
        """Extract clean domain from URL"""
        domain = urlparse(url).netloc.lower()
        return domain.replace('www.', '')
    
    def _get_linkedin_intelligence(self, company_name: str, domain: str) -> Dict[str, Any]:
        """Gather LinkedIn company intelligence"""
        try:
            # LinkedIn company search (public data only)
            search_query = f"site:linkedin.com/company {company_name}"
            linkedin_data = self._search_web(search_query, limit=3)
            
            intelligence = {
                'company_page_exists': len(linkedin_data) > 0,
                'employee_count_estimate': self._estimate_employee_count(linkedin_data),
                'recent_posts': self._extract_recent_activity(linkedin_data),
                'key_executives': self._identify_executives(company_name),
                'hiring_activity': self._detect_hiring_activity(company_name)
            }
            
            return intelligence
            
        except Exception as e:
            logger.warning(f"LinkedIn intelligence gathering failed: {e}")
            return {}
    
    def _analyze_news_sentiment(self, company_name: str) -> Dict[str, Any]:
        """Analyze recent news sentiment about the company"""
        try:
            # Search for recent news
            news_query = f'"{company_name}" (funding OR acquisition OR partnership OR launch) -site:linkedin.com -site:facebook.com'
            news_results = self._search_web(news_query, limit=10, time_filter='recent')
            
            sentiment_data = {
                'recent_news_count': len(news_results),
                'positive_signals': self._detect_positive_signals(news_results),
                'negative_signals': self._detect_negative_signals(news_results),
                'funding_news': self._extract_funding_news(news_results),
                'product_launches': self._extract_product_news(news_results),
                'partnership_news': self._extract_partnership_news(news_results)
            }
            
            # Calculate overall sentiment score
            sentiment_data['sentiment_score'] = self._calculate_sentiment_score(sentiment_data)
            
            return sentiment_data
            
        except Exception as e:
            logger.warning(f"News sentiment analysis failed: {e}")
            return {}
    
    def _get_funding_intelligence(self, company_name: str, domain: str) -> Dict[str, Any]:
        """Gather funding and financial intelligence"""
        try:
            # Search for funding information
            funding_query = f'"{company_name}" (raised OR funding OR investment OR valuation OR series) site:crunchbase.com OR site:techcrunch.com'
            funding_results = self._search_web(funding_query, limit=5)
            
            return {
                'funding_history': self._extract_funding_rounds(funding_results),
                'investors': self._extract_investor_info(funding_results),
                'valuation_estimates': self._extract_valuations(funding_results),
                'ipo_signals': self._detect_ipo_signals(funding_results),
                'acquisition_rumors': self._detect_acquisition_signals(funding_results)
            }
            
        except Exception as e:
            logger.warning(f"Funding intelligence gathering failed: {e}")
            return {}
    
    def _detect_technology_stack(self, url: str) -> Dict[str, Any]:
        """Detect technology stack used by the company"""
        try:
            # Analyze website technology
            response = self.session.get(url, timeout=10)
            headers = response.headers
            html_content = response.text.lower()
            
            tech_stack = {
                'web_server': self._detect_web_server(headers),
                'cms_platform': self._detect_cms(html_content, headers),
                'analytics_tools': self._detect_analytics(html_content),
                'marketing_tools': self._detect_marketing_tools(html_content),
                'ecommerce_platform': self._detect_ecommerce(html_content),
                'cdn_provider': self._detect_cdn(headers),
                'ssl_certificate': self._analyze_ssl(url),
                'mobile_optimization': self._check_mobile_optimization(html_content)
            }
            
            # Technology sophistication score
            tech_stack['sophistication_score'] = self._calculate_tech_sophistication(tech_stack)
            
            return tech_stack
            
        except Exception as e:
            logger.warning(f"Technology stack detection failed: {e}")
            return {}
    
    def _analyze_social_presence(self, company_name: str, domain: str) -> Dict[str, Any]:
        """Analyze social media presence and engagement"""
        try:
            social_platforms = {
                'twitter': f'site:twitter.com "{company_name}" OR site:x.com "{company_name}"',
                'facebook': f'site:facebook.com "{company_name}"',
                'instagram': f'site:instagram.com "{company_name}"',
                'youtube': f'site:youtube.com "{company_name}"'
            }
            
            presence_data = {}
            for platform, query in social_platforms.items():
                results = self._search_web(query, limit=3)
                presence_data[platform] = {
                    'has_presence': len(results) > 0,
                    'profile_urls': [r.get('url', '') for r in results[:1]],
                    'recent_activity': len(results) > 0
                }
            
            return presence_data
            
        except Exception as e:
            logger.warning(f"Social presence analysis failed: {e}")
            return {}
    
    def _identify_competitors(self, company_name: str, company_data) -> List[str]:
        """Identify potential competitors"""
        try:
            # Extract industry keywords from company content
            if isinstance(company_data, dict):
                homepage_content = company_data.get('homepage', {}).get('content', '')
                about_content = company_data.get('about', {}).get('content', '')
                content = f"{homepage_content} {about_content}"
            else:
                content = f"{company_data.homepage.content} {company_data.about.content}"
            industry_keywords = self._extract_industry_keywords(content)
            
            # Search for competitors
            competitor_query = f'competitors of "{company_name}" OR alternative to "{company_name}"'
            competitor_results = self._search_web(competitor_query, limit=5)
            
            competitors = self._extract_competitor_names(competitor_results)
            
            return competitors[:10]  # Top 10 competitors
            
        except Exception as e:
            logger.warning(f"Competitor identification failed: {e}")
            return []
    
    def _detect_growth_signals(self, company_name: str, domain: str) -> Dict[str, Any]:
        """Detect various growth and expansion signals"""
        try:
            growth_indicators = {
                'job_postings': self._count_job_postings(company_name),
                'office_expansions': self._detect_office_expansions(company_name),
                'product_releases': self._count_recent_releases(company_name),
                'press_mentions': self._count_press_mentions(company_name),
                'partnership_announcements': self._count_partnerships(company_name),
                'awards_recognition': self._find_recent_awards(company_name)
            }
            
            # Calculate growth score
            growth_indicators['growth_score'] = self._calculate_growth_score(growth_indicators)
            
            return growth_indicators
            
        except Exception as e:
            logger.warning(f"Growth signal detection failed: {e}")
            return {}
    
    def _find_key_contacts(self, company_name: str, domain: str) -> Dict[str, Any]:
        """Find key decision makers and contacts"""
        try:
            # Search for executives and decision makers
            exec_query = f'"{company_name}" (CEO OR CTO OR VP OR Director OR "Head of") site:linkedin.com'
            exec_results = self._search_web(exec_query, limit=10)
            
            contacts = {
                'executives': self._extract_executive_info(exec_results),
                'decision_makers': self._identify_decision_makers(exec_results),
                'technical_contacts': self._find_technical_contacts(company_name),
                'sales_contacts': self._find_sales_contacts(domain)
            }
            
            return contacts
            
        except Exception as e:
            logger.warning(f"Contact intelligence gathering failed: {e}")
            return {}
    
    def _search_web(self, query: str, limit: int = 10, time_filter: str = None) -> List[Dict[str, Any]]:
        """Perform web search using multiple search engines"""
        # This would integrate with search APIs like Bing, DuckDuckGo, or custom search
        # For now, returning mock structure
        
        # Note: In production, this would use actual search APIs
        # like Bing Web Search API, Google Custom Search, or SerpAPI
        
        results = []
        try:
            # Placeholder for actual search implementation
            # results = actual_search_api(query, limit, time_filter)
            logger.info(f"Searching: {query[:50]}...")
            
            # Mock results structure for development
            results = [
                {
                    'title': f'Search result for {query}',
                    'url': 'https://example.com',
                    'snippet': f'Sample content related to {query}',
                    'date': datetime.now().isoformat()
                }
            ]
            
        except Exception as e:
            logger.warning(f"Web search failed for query: {query}: {e}")
        
        return results
    
    # Helper methods for data extraction
    def _estimate_employee_count(self, linkedin_data: List[Dict]) -> str:
        """Estimate employee count from LinkedIn data"""
        # Logic to extract employee count indicators
        return "Unknown"
    
    def _extract_recent_activity(self, linkedin_data: List[Dict]) -> List[str]:
        """Extract recent LinkedIn activity"""
        return []
    
    def _identify_executives(self, company_name: str) -> List[Dict[str, str]]:
        """Identify key executives"""
        return []
    
    def _detect_hiring_activity(self, company_name: str) -> Dict[str, Any]:
        """Detect current hiring activity"""
        return {'active_hiring': False, 'open_positions': 0}
    
    def _detect_positive_signals(self, news_results: List[Dict]) -> List[str]:
        """Detect positive news signals"""
        positive_keywords = ['funding', 'growth', 'expansion', 'award', 'partnership', 'acquisition', 'launch']
        signals = []
        
        for result in news_results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
            for keyword in positive_keywords:
                if keyword in text:
                    signals.append(f"Recent {keyword} activity detected")
                    break
        
        return list(set(signals))
    
    def _detect_negative_signals(self, news_results: List[Dict]) -> List[str]:
        """Detect negative news signals"""
        negative_keywords = ['layoff', 'bankruptcy', 'lawsuit', 'scandal', 'decline', 'loss']
        signals = []
        
        for result in news_results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
            for keyword in negative_keywords:
                if keyword in text:
                    signals.append(f"Potential {keyword} concern detected")
                    break
        
        return list(set(signals))
    
    def _calculate_sentiment_score(self, sentiment_data: Dict) -> float:
        """Calculate overall sentiment score (0-100)"""
        positive_count = len(sentiment_data.get('positive_signals', []))
        negative_count = len(sentiment_data.get('negative_signals', []))
        
        if positive_count + negative_count == 0:
            return 50.0  # Neutral
        
        return (positive_count / (positive_count + negative_count)) * 100
    
    def _extract_funding_rounds(self, results: List[Dict]) -> List[Dict]:
        """Extract funding round information"""
        return []
    
    def _extract_investor_info(self, results: List[Dict]) -> List[str]:
        """Extract investor information"""
        return []
    
    def _extract_valuations(self, results: List[Dict]) -> List[Dict]:
        """Extract valuation information"""
        return []
    
    def _detect_ipo_signals(self, results: List[Dict]) -> bool:
        """Detect IPO preparation signals"""
        return False
    
    def _detect_acquisition_signals(self, results: List[Dict]) -> List[str]:
        """Detect acquisition rumors or signals"""
        return []
    
    def _detect_web_server(self, headers: Dict) -> str:
        """Detect web server from headers"""
        server = headers.get('server', '').lower()
        if 'nginx' in server:
            return 'Nginx'
        elif 'apache' in server:
            return 'Apache'
        elif 'cloudflare' in server:
            return 'Cloudflare'
        return 'Unknown'
    
    def _detect_cms(self, html: str, headers: Dict) -> str:
        """Detect CMS platform"""
        if 'wp-content' in html or 'wordpress' in html:
            return 'WordPress'
        elif 'shopify' in html or 'shopify' in str(headers):
            return 'Shopify'
        elif 'squarespace' in html:
            return 'Squarespace'
        elif 'wix' in html:
            return 'Wix'
        return 'Custom/Unknown'
    
    def _detect_analytics(self, html: str) -> List[str]:
        """Detect analytics tools"""
        tools = []
        if 'google-analytics' in html or 'gtag' in html:
            tools.append('Google Analytics')
        if 'facebook.com/tr' in html or 'fbq' in html:
            tools.append('Facebook Pixel')
        if 'hotjar' in html:
            tools.append('Hotjar')
        return tools
    
    def _detect_marketing_tools(self, html: str) -> List[str]:
        """Detect marketing automation tools"""
        tools = []
        if 'hubspot' in html:
            tools.append('HubSpot')
        if 'mailchimp' in html:
            tools.append('Mailchimp')
        if 'intercom' in html:
            tools.append('Intercom')
        return tools
    
    def _detect_ecommerce(self, html: str) -> str:
        """Detect e-commerce platform"""
        if 'shopify' in html:
            return 'Shopify'
        elif 'magento' in html:
            return 'Magento'
        elif 'woocommerce' in html:
            return 'WooCommerce'
        return 'None detected'
    
    def _detect_cdn(self, headers: Dict) -> str:
        """Detect CDN provider"""
        server = str(headers).lower()
        if 'cloudflare' in server:
            return 'Cloudflare'
        elif 'fastly' in server:
            return 'Fastly'
        elif 'amazon' in server or 'aws' in server:
            return 'Amazon CloudFront'
        return 'Unknown'
    
    def _analyze_ssl(self, url: str) -> Dict[str, Any]:
        """Analyze SSL certificate"""
        return {
            'has_ssl': url.startswith('https://'),
            'provider': 'Unknown',
            'grade': 'Unknown'
        }
    
    def _check_mobile_optimization(self, html: str) -> bool:
        """Check for mobile optimization"""
        return 'viewport' in html and 'responsive' in html
    
    def _calculate_tech_sophistication(self, tech_stack: Dict) -> int:
        """Calculate technology sophistication score (0-100)"""
        score = 0
        
        # Modern web server
        if tech_stack.get('web_server') in ['Nginx', 'Cloudflare']:
            score += 10
        
        # Analytics tools
        score += len(tech_stack.get('analytics_tools', [])) * 5
        
        # Marketing tools
        score += len(tech_stack.get('marketing_tools', [])) * 5
        
        # SSL and mobile
        if tech_stack.get('ssl_certificate', {}).get('has_ssl'):
            score += 15
        if tech_stack.get('mobile_optimization'):
            score += 15
        
        # CDN usage
        if tech_stack.get('cdn_provider') != 'Unknown':
            score += 20
        
        return min(score, 100)
    
    def _extract_industry_keywords(self, content: str) -> List[str]:
        """Extract industry-specific keywords"""
        # This would use NLP to extract relevant industry terms
        return []
    
    def _extract_competitor_names(self, results: List[Dict]) -> List[str]:
        """Extract competitor names from search results"""
        return []
    
    def _count_job_postings(self, company_name: str) -> int:
        """Count current job postings"""
        return 0
    
    def _detect_office_expansions(self, company_name: str) -> List[str]:
        """Detect recent office expansions"""
        return []
    
    def _count_recent_releases(self, company_name: str) -> int:
        """Count recent product releases"""
        return 0
    
    def _count_press_mentions(self, company_name: str) -> int:
        """Count recent press mentions"""
        return 0
    
    def _count_partnerships(self, company_name: str) -> int:
        """Count recent partnership announcements"""
        return 0
    
    def _find_recent_awards(self, company_name: str) -> List[str]:
        """Find recent awards and recognition"""
        return []
    
    def _calculate_growth_score(self, indicators: Dict) -> int:
        """Calculate overall growth score (0-100)"""
        score = 0
        score += min(indicators.get('job_postings', 0) * 2, 20)
        score += len(indicators.get('office_expansions', [])) * 10
        score += min(indicators.get('product_releases', 0) * 5, 25)
        score += min(indicators.get('press_mentions', 0), 20)
        score += min(indicators.get('partnership_announcements', 0) * 8, 24)
        score += len(indicators.get('awards_recognition', [])) * 15
        
        return min(score, 100)
    
    def _extract_executive_info(self, results: List[Dict]) -> List[Dict]:
        """Extract executive information"""
        return []
    
    def _identify_decision_makers(self, results: List[Dict]) -> List[Dict]:
        """Identify key decision makers"""
        return []
    
    def _find_technical_contacts(self, company_name: str) -> List[Dict]:
        """Find technical contacts"""
        return []
    
    def _find_sales_contacts(self, domain: str) -> List[str]:
        """Find sales contact information"""
        common_sales_emails = [
            f"sales@{domain}",
            f"info@{domain}",
            f"contact@{domain}",
            f"hello@{domain}"
        ]
        return common_sales_emails
    
    # Additional extraction methods...
    def _extract_funding_news(self, results: List[Dict]) -> List[Dict]:
        """Extract funding-related news"""
        return []
    
    def _extract_product_news(self, results: List[Dict]) -> List[Dict]:
        """Extract product launch news"""
        return []
    
    def _extract_partnership_news(self, results: List[Dict]) -> List[Dict]:
        """Extract partnership news"""
        return []


def enhance_factsheet_with_intelligence(company_data, base_factsheet: str) -> str:
    """Enhance base factsheet with deep web intelligence"""
    try:
        intelligence_engine = DeepWebIntelligence()
        intelligence = intelligence_engine.gather_intelligence(company_data)
        
        # Create intelligence summary
        intel_summary = generate_intelligence_summary(intelligence)
        
        # Insert intelligence into factsheet
        enhanced_factsheet = insert_intelligence_section(base_factsheet, intel_summary)
        
        return enhanced_factsheet
        
    except Exception as e:
        logger.warning(f"Intelligence enhancement failed: {e}")
        return base_factsheet

def generate_intelligence_summary(intelligence: Dict[str, Any]) -> str:
    """Generate a formatted intelligence summary"""
    
    summary_sections = []
    
    # Company Intelligence Section
    if intelligence.get('linkedin_data', {}).get('company_page_exists'):
        summary_sections.append("## Business Intelligence\n")
        
        linkedin = intelligence['linkedin_data']
        if linkedin.get('employee_count_estimate') != 'Unknown':
            summary_sections.append(f"**Company Size**: {linkedin['employee_count_estimate']} employees (estimated)")
        
        if linkedin.get('hiring_activity', {}).get('active_hiring'):
            summary_sections.append("**Growth Signal**: Active hiring detected - company is expanding")
    
    # News & Sentiment Section
    news_data = intelligence.get('news_sentiment', {})
    if news_data.get('recent_news_count', 0) > 0:
        summary_sections.append("## Recent News & Market Sentiment\n")
        
        sentiment_score = news_data.get('sentiment_score', 50)
        if sentiment_score > 70:
            summary_sections.append("**Market Sentiment**: Positive (recent favorable news coverage)")
        elif sentiment_score < 30:
            summary_sections.append("**Market Sentiment**: Mixed (some concerns in recent coverage)")
        else:
            summary_sections.append("**Market Sentiment**: Neutral")
        
        positive_signals = news_data.get('positive_signals', [])
        if positive_signals:
            summary_sections.append(f"**Positive Indicators**: {', '.join(positive_signals[:3])}")
    
    # Technology & Digital Maturity
    tech_stack = intelligence.get('tech_stack', {})
    if tech_stack.get('sophistication_score', 0) > 0:
        summary_sections.append("## Technology & Digital Maturity\n")
        
        score = tech_stack['sophistication_score']
        if score > 70:
            maturity = "High - Modern, sophisticated technology stack"
        elif score > 40:
            maturity = "Medium - Standard technology implementations"
        else:
            maturity = "Basic - Limited technology adoption"
        
        summary_sections.append(f"**Digital Maturity**: {maturity}")
        
        if tech_stack.get('cms_platform') != 'Custom/Unknown':
            summary_sections.append(f"**Platform**: {tech_stack['cms_platform']}")
        
        analytics_tools = tech_stack.get('analytics_tools', [])
        if analytics_tools:
            summary_sections.append(f"**Analytics Tools**: {', '.join(analytics_tools)}")
    
    # Growth Indicators
    growth_data = intelligence.get('growth_indicators', {})
    if growth_data.get('growth_score', 0) > 20:
        summary_sections.append("## Growth & Expansion Signals\n")
        
        score = growth_data['growth_score']
        if score > 60:
            growth_status = "High Growth - Multiple expansion indicators"
        elif score > 30:
            growth_status = "Moderate Growth - Some positive indicators"
        else:
            growth_status = "Stable - Limited growth signals"
        
        summary_sections.append(f"**Growth Status**: {growth_status}")
        
        job_postings = growth_data.get('job_postings', 0)
        if job_postings > 5:
            summary_sections.append(f"**Hiring Activity**: {job_postings} open positions detected")
    
    # Competitive Intelligence
    competitors = intelligence.get('competitive_landscape', [])
    if competitors:
        summary_sections.append("## Competitive Landscape\n")
        summary_sections.append(f"**Key Competitors**: {', '.join(competitors[:5])}")
    
    # Contact Intelligence
    contacts = intelligence.get('contact_intelligence', {})
    sales_contacts = contacts.get('sales_contacts', [])
    if sales_contacts:
        summary_sections.append("## Contact Intelligence\n")
        summary_sections.append(f"**Potential Sales Contacts**: {', '.join(sales_contacts[:3])}")
    
    # Funding Intelligence
    funding = intelligence.get('funding_data', {})
    if funding.get('funding_history'):
        summary_sections.append("## Financial Intelligence\n")
        summary_sections.append("**Funding Status**: Recent funding activity detected")
    
    return "\n".join(summary_sections)

def insert_intelligence_section(base_factsheet: str, intelligence_summary: str) -> str:
    """Insert intelligence summary into the base factsheet"""
    if not intelligence_summary.strip():
        return base_factsheet
    
    # Find insertion point (after Company Overview, before Products & Services)
    lines = base_factsheet.split('\n')
    insertion_point = -1
    
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('## products') or line.strip().lower().startswith('## business details'):
            insertion_point = i
            break
    
    if insertion_point == -1:
        # If no clear insertion point, add at the end
        return f"{base_factsheet}\n\n{intelligence_summary}"
    
    # Insert the intelligence summary
    enhanced_lines = (
        lines[:insertion_point] + 
        ['', intelligence_summary, ''] + 
        lines[insertion_point:]
    )
    
    return '\n'.join(enhanced_lines)