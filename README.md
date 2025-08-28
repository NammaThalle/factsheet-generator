# Company Factsheet Generator

An AI-powered Python tool that generates business intelligence factsheets from company websites for sales teams.

## Features

- **Web Scraping**: Extracts content from company homepages and About pages
- **AI-Powered Analysis**: Uses OpenAI GPT to generate structured factsheets
- **Sales-Focused**: Creates actionable intelligence for discovery calls
- **CLI Interface**: Easy-to-use command line tool
- **Batch Processing**: Process multiple companies from CSV

## Installation

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-openai-api-key-here'
   ```

## Usage

### Single Company
```bash
python src/main.py --url https://company.com/
```

### Multiple Companies from CSV
```bash
# List available companies
python src/main.py --csv companies.csv

# Process specific company by index
python src/main.py --csv companies.csv --select 0
```

### Options
- `--output-dir`: Specify output directory for factsheet files
- `--verbose`: Enable detailed logging

## Output

The tool generates markdown factsheets containing:
- **Company Overview**: Mission, value propositions, business model
- **Products & Services**: Core offerings, target markets
- **Business Intelligence**: Market positioning, company size indicators  
- **Sales Insights**: Conversation starters, potential pain points

## Sample Companies

The included `companies.csv` contains 6 sample companies across different industries:
- Construction, Retail, Manufacturing, Healthcare, Financial Services

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for web scraping