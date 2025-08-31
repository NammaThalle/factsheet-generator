# Company Factsheet Generator

An AI-powered Python tool that generates business intelligence factsheets from company websites for sales teams. Features both a modern web interface and command-line interface.

## Features

- **Web Interface**: Interactive Streamlit dashboard with real-time generation and analytics
- **REST API**: FastAPI backend with async processing and auto-generated documentation  
- **Web Scraping**: Intelligent content extraction from company homepages and About pages
- **AI-Powered Analysis**: OpenAI GPT integration
- **Sales-Focused**: Creates actionable intelligence optimized for discovery calls
- **CLI Interface**: Full-featured command line tool for automation
- **Batch Processing**: Process multiple companies from CSV files
- **Beautiful Logging**: Colored, structured logs with file:line navigation

## Quick Start

### Web Interface (Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API key:**
   ```bash
   export OPENAI_API_KEY='your-openai-api-key-here'
   ```

3. **Start web interface:**
   ```bash
   ./start-web.sh
   ```
   
   The `start-web.sh` script automatically:
   - Starts the FastAPI backend server on port 8000
   - Launches the Streamlit frontend on port 8501
   - Opens the web app in your default browser
   - Handles graceful shutdown when you press Ctrl+C

4. **Access the application:**
   - **Web App**: http://localhost:8501
   - **API Docs**: http://localhost:8000/docs

### Command Line Interface

#### Single Company
```bash
python src/main.py --url https://company.com/
```

#### Batch Processing
```bash
# List available companies
python src/main.py --csv companies.csv

# Process specific company
python src/main.py --csv companies.csv --select 0
```

#### CLI Options
- `--model`: Specific OpenAI model name (optional)
- `--model`: Specific model name (optional)
- `--output-dir`: Output directory (default: factsheets/)
- `--verbose`: Enable detailed logging

## Web Interface Features

### Dashboard
- View all generated factsheets with metadata
- Analytics charts (word count distribution, creation timeline)
- Real-time metrics (total factsheets, average words, file sizes)
- Quick actions (view, delete, download)

### Generator
- Simple URL input with validation and auto-completion
- OpenAI model selection with smart model detection
- Dropdown menus for available OpenAI models
- Real-time progress tracking with status updates
- Immediate results display

### Viewer
- Beautiful markdown rendering
- Company metadata and statistics
- One-click download functionality
- Clean, professional layout

## API Reference

### Core Endpoints
- `POST /api/generate` - Start factsheet generation
- `GET /api/tasks/{task_id}` - Check generation progress
- `GET /api/factsheets` - List all factsheets with metadata
- `GET /api/factsheets/{filename}` - Get specific factsheet content
- `DELETE /api/factsheets/{filename}` - Delete factsheet
- `GET /api/factsheets/{filename}/download` - Download file
- `GET /api/health` - Health check endpoint

### Example API Usage

**Generate factsheet:**
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stripe.com", "model": "gpt-4o-mini"}'
```

**Check progress:**
```bash
curl "http://localhost:8000/api/tasks/{task-id}"
```

**List factsheets:**
```bash
curl "http://localhost:8000/api/factsheets"
```

## Project Architecture

### Directory Structure
```
factsheet-generator/
├── src/                    # Core CLI application
│   ├── main.py            # CLI entry point
│   ├── scraper.py         # Web scraping engine
│   ├── synthesizer.py     # AI integration (OpenAI)
│   ├── logger.py          # Beautiful colored logging
│   └── models.py          # Pydantic data models
├── web/                   # Web interface
│   ├── backend/
│   │   ├── app.py         # FastAPI application
│   │   └── api/           # API routes and models
│   ├── frontend/
│   │   └── app.py         # Streamlit application
│   └── shared/
│       └── utils.py       # API client utilities
├── scripts/               # Startup utilities
│   ├── start-backend.py   # FastAPI launcher
│   └── start-frontend.py  # Streamlit launcher
├── factsheets/           # Generated factsheet files
├── companies.csv         # Sample company data
├── requirements.txt      # Python dependencies
└── start-web.sh          # One-command web startup
```

### Technology Stack
- **Backend**: FastAPI, Uvicorn, Pydantic, aiofiles
- **Frontend**: Streamlit, Plotly, Pandas
- **AI Provider**: OpenAI GPT
- **Web Scraping**: BeautifulSoup4, Requests
- **Development**: Python 3.8+, Virtual environments

## Sample Output

The tool generates 600-1000 word markdown factsheets containing:

- **Company Overview**: Mission, value propositions, business model
- **Products & Services**: Core offerings, target markets, pricing insights
- **Business Intelligence**: Market positioning, company size indicators
- **Sales Insights**: Conversation starters, potential pain points, competitive advantages
- **Key Contacts**: Leadership information and contact details (when available)

## Sample Companies

The included `companies.csv` contains 6 diverse companies for testing:
- **Construction**: Drees Homes (custom home builder)
- **Retail**: Good2Grow (children's beverages)  
- **Manufacturing**: Silk Road Medical (medical devices)
- **Healthcare**: National Care Advisors (healthcare consulting)
- **Beverages**: Tractor Beverage Co. (organic craft drinks)
- **Financial Services**: Dark Horse CPA (accounting services)

## Environment Setup

### API Keys (.env file)
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

## Development

### Running Services Separately

**Backend Development:**
```bash
# Start with auto-reload
python scripts/start-backend.py

# Or with uvicorn directly
uvicorn web.backend.app:app --reload --port 8000
```

**Frontend Development:**
```bash
# Start Streamlit
python scripts/start-frontend.py

# Or with streamlit directly
streamlit run web/frontend/app.py --server.port 8501
```

### Adding New Features

**New API Endpoint:**
1. Add route in `web/backend/api/routes.py`
2. Define models in `web/backend/api/models.py`
3. Update API client in `web/shared/utils.py`

**New Frontend Feature:**
1. Add function in `web/frontend/app.py`
2. Update navigation if needed
3. Test with backend integration

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure running from project root directory
- Check virtual environment is activated

**Port Conflicts:**
- Backend (8000): Kill existing FastAPI processes
- Frontend (8501): Kill existing Streamlit processes

**API Connection:**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check logs for detailed error information

**Missing Dependencies:**
```bash
pip install -r requirements.txt
```

### Debug Commands

```bash
# Check API health
curl http://localhost:8000/api/health

# View API documentation
open http://localhost:8000/docs

# Enable verbose CLI logging
python src/main.py --url https://example.com --verbose
```

## Performance & Security

### Optimizations
- **Async Processing**: Non-blocking factsheet generation
- **Background Tasks**: Parallel processing with progress tracking
- **Caching**: Streamlit session state management
- **Efficient Parsing**: BeautifulSoup with optimized content extraction

### Security Features
- **Input Validation**: Pydantic models prevent malformed requests
- **Secure File Handling**: Safe filename generation and file operations
- **API Key Protection**: Environment variables only, never logged
- **Error Handling**: Detailed logs without exposing system internals

## Requirements

- **Python**: 3.8+ (developed with 3.13)
- **Memory**: ~200MB for typical operation
- **Storage**: Minimal (factsheets ~5-15KB each)
- **Network**: Internet connection for web scraping and AI APIs
- **API Keys**: OpenAI account required

### Potential Enhancements
- **Database**: PostgreSQL/MongoDB for factsheet storage
- **Templates**: Industry-specific factsheet formats
- **Additional AI Providers**: Support for other LLM providers
- **Selenium Integration**: Use Selenium to load complete pages and parse with BeautifulSoup for dynamic content that loads after scrolling
- **News Article Parser**: Try newspaper3k instead of BeautifulSoup to check if it performs better for content extraction
- **Intelligent Model Selection**: Automatically pick the optimal model based on content complexity to improve cost efficiency
- **Hallucination Detection**: Add validation checks to ensure generated factsheets are grounded in scraped data without LLM hallucinations
- **Deployment**: Docker containers and cloud hosting

---

**Built with modern Python technologies for professional sales intelligence.**