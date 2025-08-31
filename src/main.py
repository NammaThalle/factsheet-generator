#!/usr/bin/env python3
"""
Company Factsheet Generator - CLI Interface

Generates AI-powered business intelligence factsheets from company websites
for sales teams preparing for discovery calls.
"""

import argparse
import csv
import sys
import os
from pathlib import Path

from scraper import scrape_company_data
from synthesizer import create_factsheet
from logger import logger

def sanitize_filename(title: str, fallback_url: str = "") -> str:
    """Create a safe filename from company domain"""
    from urllib.parse import urlparse
    
    if fallback_url:
        domain = urlparse(fallback_url).netloc
        domain = domain.replace('www.', '').replace('app.', '').replace('api.', '')
        company_name = domain.split('.')[0].lower().replace('-', '').replace('_', '')
        return f"{company_name}.md"
    else:
        return "factsheet.md"

def load_companies(csv_file):
    """Load company data from CSV file"""
    companies = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                companies.append({
                    'url': row['URL'].strip(),
                    'industry': row['Industry'].strip()
                })
    except Exception as e:
        logger.error(f"Error loading companies from {csv_file}: {str(e)}")
        return []
    return companies

def generate_factsheet_for_company(url, output_dir="factsheets", model=None):
    """Generate factsheet for a single company"""
    logger.info(f"Starting factsheet generation for: {url}")
    
    # Step 1: Scrape company data
    logger.step(1, "Scraping company website...")
    company_data = scrape_company_data(url)
    
    if not company_data['success']:
        logger.error(f"Failed to scrape data from {url}")
        return False
    
    # Step 2: Generate factsheet
    logger.step(2, "Generating factsheet with OpenAI...")
    factsheet_content = create_factsheet(company_data, model=model)
    
    if not factsheet_content:
        logger.error("Failed to generate factsheet")
        return False
    
    # Step 3: Save factsheet
    page_title = company_data['homepage'].get('title', '')
    filename = sanitize_filename(page_title, url)
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    output_path = Path(output_dir) / filename
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(factsheet_content)
        logger.success(f"Factsheet saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving factsheet: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate company factsheets from web data using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --url https://company.com/
  python src/main.py --csv companies.csv --select 0
  python src/main.py --url https://company.com/ --provider openai
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--url', type=str, help='Single company URL to process')
    input_group.add_argument('--csv', type=str, default='companies.csv', 
                           help='CSV file containing company URLs')
    
    parser.add_argument('--select', type=int, help='Select specific company index from CSV (0-based)')
    parser.add_argument('--output-dir', type=str, default='factsheets', 
                       help='Output directory for factsheet files')
    parser.add_argument('--model', type=str, help='OpenAI model to use (e.g., gpt-4o-mini, gpt-4o)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.set_verbose(True)
    
    # Validate OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY environment variable not set")
        logger.info("Please set your OpenAI API key:")
        logger.info("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Process single URL
    if args.url:
        success = generate_factsheet_for_company(args.url, args.output_dir, args.model)
        return 0 if success else 1
    
    # Process from CSV
    if args.csv:
        companies = load_companies(args.csv)
        if not companies:
            logger.error(f"No companies loaded from {args.csv}")
            return 1
        
        logger.info(f"Loaded {len(companies)} companies from {args.csv}")
        
        if args.select is not None:
            if 0 <= args.select < len(companies):
                company = companies[args.select]
                logger.info(f"Processing selected company {args.select}: {company['url']}")
                success = generate_factsheet_for_company(
                    company['url'], args.output_dir, args.model)
                return 0 if success else 1
            else:
                logger.error(f"Invalid selection {args.select}. Available indices: 0-{len(companies)-1}")
                return 1
        else:
            # List companies for selection
            logger.info("Available companies:")
            for i, company in enumerate(companies):
                logger.info(f"  {i}: {company['url']} ({company['industry']})")
            logger.info("Use --select <index> to process a specific company")
            return 0

if __name__ == "__main__":
    sys.exit(main())