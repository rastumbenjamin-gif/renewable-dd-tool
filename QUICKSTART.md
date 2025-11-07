# Quick Start Guide - Renewable DD Tool

Get the Renewable Energy Due Diligence Management Tool up and running in 15 minutes.

## Prerequisites Checklist

- [ ] Python 3.11 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] PostgreSQL 14+ installed and running
- [ ] Redis 7+ installed and running
- [ ] Google Cloud account (free tier works)
- [ ] OpenAI API key (get from https://platform.openai.com)

## Step 1: Clone and Setup (2 minutes)

```bash
# Navigate to your projects directory
cd /path/to/your/projects

# The project is already created at:
cd ~/renewable-dd-tool

# Or clone if from a repository:
# git clone <repository-url> renewable-dd-tool
# cd renewable-dd-tool
```

## Step 2: Google Cloud Setup (5 minutes)

### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Create Project" → Name it "Renewable DD Dev"
3. Enable required APIs:

```bash
gcloud services enable \
  drive.googleapis.com \
  cloudkms.googleapis.com
```

### Set Up OAuth 2.0

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Choose **Web application**
4. Add redirect URIs:
   - `http://localhost:3000/auth/callback`
5. Download credentials JSON → Save as `config/google_credentials.json`

### Create Service Account (for KMS)

```bash
# Create service account
gcloud iam service-accounts create renewable-dd-dev-sa

# Grant KMS permissions (if using KMS)
gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
  --member="serviceAccount:renewable-dd-dev-sa@[YOUR_PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

# Create key
gcloud iam service-accounts keys create ~/renewable-dd-sa-key.json \
  --iam-account=renewable-dd-dev-sa@[YOUR_PROJECT_ID].iam.gserviceaccount.com
```

## Step 3: Database Setup (3 minutes)

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql:
CREATE DATABASE renewable_dd_dev;
CREATE USER dd_user WITH PASSWORD 'dev_password_123';
GRANT ALL PRIVILEGES ON DATABASE renewable_dd_dev TO dd_user;
\q
```

### Start Redis

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Windows
redis-server
```

## Step 4: Backend Setup (3 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
# Application
APP_NAME=Renewable DD Tool
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production-12345678
SESSION_TIMEOUT_MINUTES=15

# Database
DATABASE_URL=postgresql://dd_user:dev_password_123@localhost:5432/renewable_dd_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Cloud (update with your values)
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=../config/google_credentials.json

# OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Vector DB (optional for dev)
VECTOR_DB_TYPE=chromadb  # Use chromadb for local dev
# PINECONE_API_KEY=your-pinecone-key  # Only if using Pinecone

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=  # Leave empty for dev
EOF

# Initialize database
alembic upgrade head

# Run backend
uvicorn api.main:app --reload --port 8000
```

Backend should now be running at: http://localhost:8000

## Step 5: Frontend Setup (2 minutes)

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
EOF

# Run frontend
npm run dev
```

Frontend should now be running at: http://localhost:3000

## Step 6: Verify Installation (1 minute)

### Check Backend

Visit: http://localhost:8000/health

Should see:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### Check API Docs

Visit: http://localhost:8000/docs

You should see the interactive API documentation (Swagger UI)

### Check Frontend

Visit: http://localhost:3000

You should see the login page with "Sign in with Google" button

## Step 7: Create First Project (Optional)

### Login

1. Click "Sign in with Google"
2. Select your Google account
3. Grant permissions

### Create Test Project

1. Click "New Project"
2. Fill in:
   - **Name**: Test Solar Project
   - **Technology**: Solar
   - **Capacity**: 50 MW
   - **Location**: California
3. Click "Create"

### Upload Test Document

1. Navigate to "Documents" tab
2. Upload a sample PDF (any PDF for testing)
3. Select category: "Commercial"
4. Watch it process and classify

## Common Issues & Solutions

### Issue: "Module not found" errors

**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Issue: Database connection failed

**Solution:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Verify credentials in .env match your database
# DATABASE_URL=postgresql://dd_user:dev_password_123@localhost:5432/renewable_dd_dev
```

### Issue: Redis connection failed

**Solution:**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if not running
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Issue: Google OAuth not working

**Solution:**
1. Verify OAuth credentials in Google Cloud Console
2. Check redirect URI exactly matches: `http://localhost:3000/auth/callback`
3. Ensure `GOOGLE_CLIENT_ID` matches in both backend `.env` and frontend `.env.local`

### Issue: OpenAI API errors

**Solution:**
```bash
# Verify API key is valid
# Test with curl:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Update .env with correct key:
OPENAI_API_KEY=sk-your-actual-key
```

### Issue: Port already in use

**Solution:**
```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill the process or use different port
# Backend:
uvicorn api.main:app --reload --port 8001

# Frontend:
PORT=3001 npm run dev
```

## Next Steps

### For Development

1. **Read the docs**:
   - [API Documentation](docs/API_DOCUMENTATION.md)
   - [User Guide](docs/USER_GUIDE.md)
   - [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

2. **Explore the codebase**:
   - Backend: Start with `backend/api/main.py`
   - Frontend: Start with `frontend/pages/index.tsx`
   - Models: Check `backend/models/`

3. **Run tests**:
   ```bash
   # Backend
   cd backend
   pytest tests/ -v

   # Frontend
   cd frontend
   npm test
   ```

### For Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete production deployment instructions.

## Development Workflow

### Making Changes

1. **Backend changes**:
   - Edit Python files in `backend/`
   - Changes auto-reload (FastAPI reload enabled)
   - Test endpoints at http://localhost:8000/docs

2. **Frontend changes**:
   - Edit TypeScript/React files in `frontend/`
   - Changes auto-reload (Next.js hot reload)
   - View at http://localhost:3000

3. **Database changes**:
   ```bash
   # Create migration
   cd backend
   alembic revision --autogenerate -m "Description"

   # Apply migration
   alembic upgrade head
   ```

### Debugging

**Backend:**
```python
# Add breakpoints in code
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json
```

**Frontend:**
```javascript
// Use browser DevTools
console.log('Debug info:', data);

// Or use VS Code debugger
```

**Logs:**
```bash
# Backend logs are in console with structured logging
# Check backend terminal for detailed logs

# Frontend logs in browser console
# Open DevTools (F12) → Console tab
```

## Useful Commands

### Backend

```bash
# Run with different log level
LOG_LEVEL=DEBUG uvicorn api.main:app --reload

# Run tests with coverage
pytest tests/ --cov --cov-report=html

# Format code
black . && isort .

# Type checking
mypy .
```

### Frontend

```bash
# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npx prettier --write .
```

### Database

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Show current revision
alembic current

# Downgrade
alembic downgrade -1

# Reset database
alembic downgrade base
alembic upgrade head
```

## Getting Help

### Resources
- **Documentation**: Check `docs/` folder
- **API Docs**: http://localhost:8000/docs
- **Code Comments**: Extensive inline documentation

### Support
- **Issues**: Create issue in project repository
- **Email**: dev-team@your-domain.com

## Environment Variables Reference

### Backend (.env)

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT signing key
- `GOOGLE_CLIENT_ID` - OAuth client ID
- `GOOGLE_CLIENT_SECRET` - OAuth client secret
- `OPENAI_API_KEY` - OpenAI API key

Optional:
- `SENTRY_DSN` - Error monitoring
- `PINECONE_API_KEY` - Vector database
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

### Frontend (.env.local)

Required:
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID` - OAuth client ID (must match backend)

## Success Checklist

After setup, you should be able to:

- [ ] Access backend at http://localhost:8000
- [ ] View API docs at http://localhost:8000/docs
- [ ] Access frontend at http://localhost:3000
- [ ] Sign in with Google account
- [ ] Create a new project
- [ ] Upload a document
- [ ] View DD checklist
- [ ] Ask questions in Q&A interface

## What's Next?

Now that you have the tool running:

1. **Try the demo workflow**:
   - Create a project
   - Upload sample documents (PPAs, permits, etc.)
   - Watch automatic classification
   - Review extracted terms
   - Ask questions in Q&A
   - Generate executive summary

2. **Customize for your needs**:
   - Add custom document types
   - Modify checklist items
   - Adjust extraction rules
   - Customize UI branding

3. **Deploy to production** (when ready):
   - Follow [DEPLOYMENT.md](docs/DEPLOYMENT.md)
   - Set up monitoring
   - Configure backups
   - Run security audit

---

**Estimated Setup Time**: 15 minutes
**Difficulty Level**: Intermediate
**Support**: dev-team@your-domain.com

Happy developing! 🚀
