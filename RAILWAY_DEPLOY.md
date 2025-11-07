# Deploy to Railway - Full Version

Railway handles large dependencies better than Render and is still free for moderate usage.

## Deploy Backend on Railway

### Step 1: Sign up for Railway
1. Go to https://railway.app
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your repositories

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `rastumbenjamin-gif/renewable-dd-tool`
4. Railway will detect both frontend and backend

### Step 3: Configure Backend Service
1. Railway will show you the detected services
2. Select the **backend** service
3. Click "Add variables" and add:
   - `OPENAI_API_KEY` = your OpenAI key
   - `PORT` = 8000
4. Railway will auto-detect Python and install from requirements.txt
5. Click "Deploy"

### Step 4: Get Backend URL
1. Once deployed, go to your backend service
2. Click "Settings" → "Generate Domain"
3. Copy the URL (e.g., `https://renewable-dd-backend-production.up.railway.app`)

### Step 5: Update Frontend on Netlify
1. Go to Netlify → Your site → Environment variables
2. Add: `NEXT_PUBLIC_API_URL` = your Railway backend URL
3. Trigger redeploy

## Why Railway?
- **Better resources**: Handles PyTorch and large ML libraries
- **Free tier**: $5 free credit per month (enough for development)
- **Auto-deploy**: Pushes to GitHub auto-deploy
- **No sleep**: Services don't sleep like Render free tier

## Alternative: DigitalOcean App Platform

If Railway doesn't work, try DigitalOcean:
1. Go to https://cloud.digitalocean.com/apps
2. Create app from GitHub
3. Configure backend with Python
4. More expensive but very reliable ($5/month minimum)

## Alternative: Run Backend Locally, Frontend on Netlify

Keep it simple during development:
1. Run backend locally: `cd backend && uvicorn api.main:app --reload`
2. Use ngrok to expose local backend: `ngrok http 8000`
3. Add ngrok URL to Netlify as `NEXT_PUBLIC_API_URL`
4. Frontend on Netlify works with your local backend

This is actually great for development because:
- No deployment wait times
- Easy debugging
- Full control over dependencies
- Can see all logs in real-time
