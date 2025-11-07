# Renewable DD Tool - Backend

FastAPI backend for the Renewable Energy Due Diligence Tool.

## Features
- Document upload and processing
- AI-powered Q&A with OpenAI
- PDF text extraction
- Progress tracking
- RESTful API

## Deployment Options

### Hugging Face Spaces (Recommended - 100% Free)
See [HUGGINGFACE_DEPLOY.md](../HUGGINGFACE_DEPLOY.md)

### Railway
See [RAILWAY_DEPLOY.md](../RAILWAY_DEPLOY.md)

### Local Development
```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

## Environment Variables
- `OPENAI_API_KEY` - Required for Q&A functionality
- `PORT` - Server port (default: 8000)
- `DATABASE_URL` - Database connection string (optional)
