# Factsheet Generator Web Interface

A modern web interface for the AI-powered company factsheet generator, built with FastAPI backend and Streamlit frontend.

## Features

### Web Dashboard
- **Interactive Dashboard**: View all generated factsheets with analytics
- **Real-time Generation**: Generate factsheets with live progress tracking
- **Beautiful Viewer**: Read factsheets with clean markdown rendering
- **Export Options**: Download factsheets as markdown files
- **Search & Filter**: Find factsheets by company name or date

### Technical Stack
- **Backend**: FastAPI with async processing
- **Frontend**: Streamlit with modern UI components
- **AI Integration**: Gemini 2.0 Flash & OpenAI GPT models
- **Data Validation**: Pydantic models for type safety
- **Logging**: Colored, structured logging system

## Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment activated
- API keys configured (Gemini/OpenAI)

### Start Web Interface
```bash
# Install web dependencies
pip install -r requirements-web.txt

# Start both backend and frontend
./start-web.sh
```

Or start services separately:

```bash
# Terminal 1: Start API Backend
python scripts/start-backend.py

# Terminal 2: Start Web Frontend  
python scripts/start-frontend.py
```

### Access the Interface
- **Web App**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Web Interface Guide

### 1. Dashboard
- View all generated factsheets
- Analytics charts (word count distribution, creation timeline)
- Metrics overview (total factsheets, average words, file sizes)
- Quick actions (view, delete factsheets)

### 2. Generator
- Enter company website URL
- Select AI provider (Gemini or OpenAI)
- Real-time progress tracking
- Immediate results with word count

### 3. Viewer
- Beautiful markdown rendering
- Company metadata display
- Download functionality
- Clean, readable layout

## API Endpoints

### Core Endpoints
- `POST /api/generate` - Start factsheet generation
- `GET /api/tasks/{task_id}` - Check generation progress
- `GET /api/factsheets` - List all factsheets
- `GET /api/factsheets/{filename}` - Get specific factsheet
- `DELETE /api/factsheets/{filename}` - Delete factsheet
- `GET /api/factsheets/{filename}/download` - Download file

### Request Examples

Generate factsheet:
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stripe.com", "provider": "gemini"}'
```

Check task status:
```bash
curl "http://localhost:8000/api/tasks/task-id-here"
```

List factsheets:
```bash
curl "http://localhost:8000/api/factsheets"
```

## Architecture

### Backend (FastAPI)
```
web/backend/
├── app.py              # Main FastAPI application
├── api/
│   ├── routes.py       # API endpoints
│   └── models.py       # Pydantic request/response models
└── __init__.py
```

### Frontend (Streamlit)
```
web/frontend/
├── app.py              # Main Streamlit application
├── pages/              # Multi-page components (future)
└── components/         # Reusable UI components (future)
```

### Shared Utilities
```
web/shared/
└── utils.py            # API client and helper functions
```

## Development

### Adding New Features

1. **New API Endpoint**:
   - Add route in `web/backend/api/routes.py`
   - Define models in `web/backend/api/models.py`
   - Update frontend client in `web/shared/utils.py`

2. **New Frontend Page**:
   - Add page function in `web/frontend/app.py`
   - Update navigation in main function
   - Create reusable components as needed

### Running in Development
- Backend auto-reloads on file changes
- Frontend updates in real-time
- Logs display in terminal with colors

## Production Deployment

### Docker (Future)
```dockerfile
# Dockerfile example for production
FROM python:3.9-slim

WORKDIR /app
COPY requirements-web.txt .
RUN pip install -r requirements-web.txt

COPY . .
EXPOSE 8000 8501

CMD ["./start-web.sh"]
```

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional
FACTSHEETS_DIR=factsheets
API_HOST=0.0.0.0
API_PORT=8000
WEB_PORT=8501
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from project root
2. **Port Conflicts**: Change ports in startup scripts if needed
3. **API Offline**: Check backend is running on port 8000
4. **Missing Dependencies**: Run `pip install -r requirements-web.txt`

### Debug Mode
```bash
# Enable verbose logging
python scripts/start-backend.py --log-level debug

# Check API health
curl http://localhost:8000/api/health
```

## Performance

### Optimization Features
- Async processing for non-blocking operations
- Background task execution
- Streamlit caching for repeated operations
- Efficient file handling with aiofiles

### Monitoring
- Health check endpoint for uptime monitoring
- Structured logging for debugging
- Real-time progress tracking
- Error handling with detailed messages

## Security

### Best Practices Implemented
- No API keys in code or logs
- Input validation with Pydantic
- Secure file handling
- CORS configured for local development
- Error messages don't expose system details

## Next Steps

### Potential Enhancements
- User authentication and sessions
- Bulk CSV upload processing
- Factsheet templates and customization
- Database integration (PostgreSQL/MongoDB)
- Caching layer (Redis)
- Container deployment (Docker/Kubernetes)
- Advanced analytics and reporting

---

**Built with modern Python web technologies for a professional, scalable solution.**