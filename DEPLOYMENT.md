# Deployment Guide

## Quick Deploy Options

### Option 1: Vercel (Frontend) + Render (Backend) - Recommended

#### Frontend on Vercel (Free)
1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your GitHub repository
4. Vercel will auto-detect Next.js
5. Set root directory to `frontend`
6. Add environment variable: `NEXT_PUBLIC_API_URL=<your-backend-url>`
7. Deploy!

#### Backend on Render (Free tier available)
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Set:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `OPENAI_API_KEY=<your-key>`
   - Other variables from `.env.example`
6. Deploy!

### Option 2: Railway (Full Stack)
1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub
3. Railway will detect both services
4. Configure environment variables
5. Deploy both frontend and backend

### Option 3: Local Deployment for Colleagues

If your colleagues want to run it locally:

```bash
# Clone the repository
git clone <your-repo-url>
cd renewable-dd-tool

# Backend setup
cd backend
pip install -r requirements.txt
cp ../config/.env.example .env
# Edit .env with your OpenAI API key
uvicorn api.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## Environment Variables Required

### Backend
- `OPENAI_API_KEY` - Your OpenAI API key (required for Q&A)
- `DATABASE_URL` - Database connection (optional, defaults to SQLite)
- `SECRET_KEY` - JWT secret (auto-generated if not set)

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL (defaults to http://localhost:8000)

## GitHub Pages Note

**Important**: GitHub Pages only hosts static HTML/CSS/JS files. This application requires:
- A backend server (FastAPI) running Python
- A frontend server (Next.js)

Therefore, GitHub Pages alone cannot host this application. Use one of the deployment options above instead.

## Cost Estimate
- **Free tier option**: Vercel (Frontend) + Render (Backend) + OpenAI API (pay per use)
- **Estimated monthly cost**: $0-10 for low usage (mostly OpenAI API costs)

## Security Notes
- Never commit `.env` files with real API keys
- Use environment variables for all secrets
- Enable HTTPS in production (Vercel/Render do this automatically)
