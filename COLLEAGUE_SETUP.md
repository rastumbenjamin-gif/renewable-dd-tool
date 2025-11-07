# Setup Guide for Colleagues

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/renewable-dd-tool.git
cd renewable-dd-tool
```

### Step 2: Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp ../config/.env.example .env

# Edit .env and add your OpenAI API key
# You can use nano, vim, or any text editor:
nano .env
# Add this line:
# OPENAI_API_KEY=sk-your-actual-key-here

# Start the backend server
uvicorn api.main:app --reload
```

Backend will run at: http://localhost:8000

### Step 3: Frontend Setup (New Terminal Window)

```bash
cd frontend

# Install Node dependencies
npm install

# Start the frontend server
npm run dev
```

Frontend will run at: http://localhost:3000

### Step 4: Access the Application

Open your browser and go to: http://localhost:3000

## Features

1. **Document Upload**
   - Go to the "Documents" tab
   - Drag & drop PDF files or click to upload
   - Select a category (Technical, Commercial, Financial, Legal, Environmental)
   - Documents persist across navigation

2. **DD Progress**
   - View the "DD Progress" tab
   - See progress by category based on uploaded documents
   - Progress updates automatically when documents are uploaded

3. **Q&A Assistant**
   - Go to the "Q&A Assistant" tab
   - Ask questions about your uploaded documents
   - AI will extract relevant information and provide sourced answers
   - Example questions:
     - "What is the PPA price?"
     - "Summarize the key risks"
     - "What documents mention interconnection?"

## Troubleshooting

### Backend won't start
- Make sure you're in the `backend` directory
- Check that Python 3.9+ is installed: `python --version`
- Verify dependencies are installed: `pip install -r requirements.txt`

### Frontend won't start
- Make sure you're in the `frontend` directory
- Check that Node.js 18+ is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Q&A not working
- Make sure your OpenAI API key is set in `backend/.env`
- Check that the backend is running on port 8000
- Upload some documents first before asking questions

### Documents not showing up
- Check backend logs for errors
- Make sure the `backend/uploads` directory exists
- Try refreshing the page

## Need Help?

Contact the repository owner or check the logs:
- Backend logs: Terminal where `uvicorn` is running
- Frontend logs: Terminal where `npm run dev` is running
- Browser console: Press F12 in your browser

## Cost Note

This application uses OpenAI's API which charges per use. Typical costs:
- Each question: ~$0.001-0.01 depending on document size
- Monthly cost with moderate use: $5-20
