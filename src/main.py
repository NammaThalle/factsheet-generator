#!/usr/bin/env python3

"""Company Factsheet Generator - Main CLI Interface"""

import argparse
import csv
import sys
import os
import logging
from pathlib import Path

from scraper import scrape_company_data
from synthesizer import create_factsheet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def generate_factsheet_for_company(url, output_dir="factsheets", provider="gemini", model=None):
    """Generate factsheet for a single company"""
    logger.info(f"Starting factsheet generation for: {url}")
    
    # Step 1: Scrape company data
    logger.info("Step 1: Scraping company website...")
    company_data = scrape_company_data(url)
    
    if not company_data['success']:
        logger.error(f"Failed to scrape data from {url}")
        return False
    
    # Step 2: Generate factsheet
    logger.info(f"Step 2: Generating factsheet with {provider.upper()}...")
    factsheet_content = create_factsheet(company_data, provider=provider, model=model)
    
    if not factsheet_content:
        logger.error("Failed to generate factsheet")
        return False
    
    # Step 3: Save factsheet
    company_name = company_data['homepage'].get('title', url.split('//')[-1].split('/')[0])
    filename = f"{company_name.lower().replace(' ', '-').replace(':', '').replace('?', '').replace('!', '').replace('(', '').replace(')', '')}.md"
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    output_path = Path(output_dir) / filename
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(factsheet_content)
        logger.info(f"Factsheet saved to: {output_path}")
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
    parser.add_argument('--provider', type=str, default='gemini', 
                       choices=['openai', 'gemini'],
                       help='AI provider to use (default: gemini - free tier available)')
    parser.add_argument('--model', type=str, help='AI model to use (provider-specific)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate API key based on provider
    if args.provider == "openai":
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OPENAI_API_KEY environment variable not set")
            logger.info("Please set your OpenAI API key:")
            logger.info("export OPENAI_API_KEY='your-api-key-here'")
            return 1
    elif args.provider == "gemini":
        if not os.getenv('GEMINI_API_KEY'):
            logger.error("GEMINI_API_KEY environment variable not set")
            logger.info("Please set your Gemini API key:")
            logger.info("export GEMINI_API_KEY='your-api-key-here'")
            return 1
    
    # Process single URL
    if args.url:
        success = generate_factsheet_for_company(args.url, args.output_dir, args.provider, args.model)
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
                    company['url'], args.output_dir, args.provider, args.model)
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