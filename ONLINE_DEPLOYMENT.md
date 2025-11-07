# Deploy Online - Step by Step Guide

Your code is now at: https://github.com/rastumbenjamin-gif/renewable-dd-tool

## Recommended: Vercel (Frontend) + Render (Backend)

This setup is **100% free** for low/moderate usage and takes ~15 minutes.

---

## Part 1: Deploy Backend on Render (5 minutes)

### Step 1: Sign up for Render
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account

### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub account if prompted
3. Select repository: `rastumbenjamin-gif/renewable-dd-tool`
4. Click "Connect"

### Step 3: Configure Service
Fill in these settings:

- **Name**: `renewable-dd-backend` (or any name you want)
- **Root Directory**: `backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables
Click "Advanced" → "Add Environment Variable"

**Required:**
- Key: `OPENAI_API_KEY`
- Value: `sk-your-actual-openai-key-here`

**Optional but recommended:**
- Key: `SECRET_KEY`
- Value: (any random string, e.g., `your-secret-key-12345`)

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 3-5 minutes for deployment
3. Once deployed, you'll see a URL like: `https://renewable-dd-backend.onrender.com`
4. **SAVE THIS URL** - you'll need it for the frontend!

### Step 6: Test Backend
Visit: `https://your-backend-url.onrender.com/health`

You should see: `{"status":"healthy"}`

---

## Part 2: Deploy Frontend on Vercel (5 minutes)

### Step 1: Sign up for Vercel
1. Go to https://vercel.com
2. Click "Sign Up"
3. Sign up with your GitHub account

### Step 2: Import Project
1. Click "Add New..." → "Project"
2. Import `rastumbenjamin-gif/renewable-dd-tool`
3. Click "Import"

### Step 3: Configure Project
Fill in these settings:

- **Framework Preset**: Next.js (auto-detected)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)

### Step 4: Add Environment Variable
Click "Environment Variables"

- Key: `NEXT_PUBLIC_API_URL`
- Value: `https://your-backend-url.onrender.com` (from Part 1, Step 5)

### Step 5: Deploy
1. Click "Deploy"
2. Wait 2-3 minutes
3. Once deployed, you'll see: "Congratulations! Your project is live!"
4. You'll get a URL like: `https://renewable-dd-tool.vercel.app`

---

## Part 3: Update Backend CORS (2 minutes)

The backend needs to allow requests from your frontend domain.

### Option A: Update via GitHub
1. Go to your repository: https://github.com/rastumbenjamin-gif/renewable-dd-tool
2. Edit `backend/api/main.py`
3. Find the CORS section (around line 25):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # <-- Change this line
    ...
)
```

4. Change to:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://renewable-dd-tool.vercel.app",  # Your Vercel URL
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],
    ...
)
```

5. Commit the change
6. Render will auto-deploy the update (takes 2-3 minutes)

---

## Your Live Application!

**Frontend URL**: https://renewable-dd-tool.vercel.app
**Backend URL**: https://renewable-dd-backend.onrender.com

Share the frontend URL with your colleagues!

---

## Important Notes

### Free Tier Limitations
- **Render Free Tier**:
  - Backend sleeps after 15 minutes of inactivity
  - First request after sleep takes ~30 seconds to wake up
  - 750 hours/month free (enough for 24/7 usage)

- **Vercel Free Tier**:
  - Unlimited bandwidth
  - 100 GB-hours compute/month
  - Perfect for this use case

### Costs
- **Hosting**: $0 (using free tiers)
- **OpenAI API**: Pay per use
  - ~$0.001-0.01 per question
  - Estimated: $5-20/month with moderate usage

### Keeping Backend Awake (Optional)
If the 30-second wake-up delay bothers you:

1. Sign up for free monitoring at https://uptimerobot.com
2. Add monitor for: `https://your-backend-url.onrender.com/health`
3. Check every 10 minutes
4. This keeps your backend awake 24/7

---

## Troubleshooting

### Frontend shows "Failed to fetch"
- Check that `NEXT_PUBLIC_API_URL` environment variable is set correctly in Vercel
- Make sure CORS is configured properly in `backend/api/main.py`
- Redeploy frontend after changing environment variables

### Backend shows 503 errors
- Check environment variables on Render (especially `OPENAI_API_KEY`)
- View logs on Render dashboard
- Make sure all dependencies installed correctly

### Q&A returns errors
- Verify OpenAI API key is correct
- Check you have credits in your OpenAI account
- Upload documents before asking questions

---

## Upgrade Options (When You Need More)

### If you outgrow free tier:

**Render Pro** ($7/month):
- No sleep/wake delay
- More compute power
- Better for production

**Vercel Pro** ($20/month):
- More build time
- Better analytics
- Custom domains

**Or migrate to:**
- AWS/Google Cloud (more complex, more powerful)
- Railway (similar to Render, different pricing)
- DigitalOcean App Platform

---

## Questions?

Check the logs:
- **Render**: Dashboard → Your Service → "Logs" tab
- **Vercel**: Dashboard → Your Project → "Deployments" → Click deployment → "Logs"

Repository: https://github.com/rastumbenjamin-gif/renewable-dd-tool
