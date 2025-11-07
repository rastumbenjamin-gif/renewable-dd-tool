# Renewable Energy Due Diligence Management Tool

A comprehensive platform for managing due diligence processes in renewable energy asset transactions (solar, wind, hydro, battery storage).

## Features

- **Document Intelligence**: Automated parsing and analysis of PPAs, interconnection agreements, permits, and more
- **Process Tracking**: Visual dashboard with completion status and responsibility tracking
- **Executive Summary**: Auto-generated reports with key findings and risk assessment
- **Q&A Interface**: Intelligent chat system for querying the data room
- **Google Drive Integration**: Seamless document management and version control
- **Enterprise Security**: End-to-end encryption, zero data retention, role-based access control

## Technology Stack

### Backend
- Python 3.11+
- FastAPI for REST API
- LangChain for document processing and RAG
- Google Drive API v3
- PostgreSQL for metadata storage
- Redis for session management
- Google Cloud KMS for encryption

### Frontend
- React 18 with TypeScript
- Next.js 14 for SSR
- TailwindCSS for styling
- Recharts for data visualization
- React Query for state management

## Project Structure

```
renewable-dd-tool/
├── backend/
│   ├── api/                    # FastAPI routes and endpoints
│   ├── document_processor/     # Document parsing and extraction
│   ├── security/               # Authentication, encryption, access control
│   ├── google_drive_integration/ # Google Drive API integration
│   ├── models/                 # Database models
│   └── utils/                  # Helper functions
├── frontend/
│   ├── components/             # React components
│   ├── pages/                  # Next.js pages
│   ├── services/               # API clients
│   └── styles/                 # CSS and styling
├── config/                     # Configuration files
├── tests/                      # Test suites
│   ├── unit/
│   ├── integration/
│   └── security/
└── docs/                       # Documentation
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Google Cloud Project with Drive API enabled

### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp config/.env.example config/.env
# Edit .env with your credentials
```

4. Initialize database:
```bash
python -m alembic upgrade head
```

5. Run development server:
```bash
uvicorn api.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Run development server:
```bash
npm run dev
```

## Google Drive Integration Setup

1. Go to Google Cloud Console
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs
6. Download credentials and place in `config/google_credentials.json`

## Security Configuration

- All documents are processed in-memory only
- No document contents are logged
- Session timeout: 15 minutes
- Encryption: AES-256-GCM via Google Cloud KMS
- Audit logs stored for 7 years (configurable)

## Usage

1. **Login**: Use Google SSO to authenticate
2. **Create Project**: Set up a new DD process
3. **Upload Documents**: Connect to Google Drive folder or upload directly
4. **Review Dashboard**: Track progress across categories
5. **Ask Questions**: Use Q&A interface to query documents
6. **Generate Reports**: Export executive summaries and findings

## API Documentation

Once running, access API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov

# Frontend tests
cd frontend
npm test

# Security tests
cd tests/security
python run_security_tests.py
```

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment instructions.

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact: [support email]
