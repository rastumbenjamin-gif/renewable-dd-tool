# Deploy to Netlify - Updated Instructions

Your code is updated and ready for Netlify!

## Netlify Settings (Use These Exact Settings)

### Site Settings:
1. **Base directory**: `frontend`
2. **Build command**: `npm run build`
3. **Publish directory**: `frontend/.next`
4. **Node version**: `18`

### Environment Variables:
Add this in Netlify dashboard under "Site configuration" → "Environment variables":
- **Key**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://your-backend-url.onrender.com` (add this after deploying backend)

## Step by Step

### 1. Deploy Backend First (Render)
Go to https://render.com and deploy the backend:
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `OPENAI_API_KEY=your-key`

Save the backend URL (e.g., `https://renewable-dd-backend.onrender.com`)

### 2. Deploy Frontend on Netlify
1. Go to https://app.netlify.com/start
2. Click "Import from Git" → "GitHub"
3. Authorize Netlify to access your repositories
4. Select `rastumbenjamin-gif/renewable-dd-tool`
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next`
6. Click "Show advanced" → "New variable"
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: Your backend URL from step 1
7. Click "Deploy site"

### 3. After Deployment
Once deployed, Netlify will give you a URL like:
`https://amazing-name-123456.netlify.app`

If you get a 404 error:
1. Go to Netlify dashboard → Your site
2. Click "Site configuration" → "Build & deploy"
3. Verify the publish directory is set to: `frontend/.next`
4. Click "Trigger deploy" → "Clear cache and deploy site"

### 4. Update Backend CORS
Edit the backend to allow your Netlify URL:
1. Go to your GitHub repository
2. Edit `backend/api/main.py`
3. Update the CORS origins:
```python
allow_origins=[
    "http://localhost:3000",
    "https://*.netlify.app",  # Allow all Netlify domains
]
```
4. Commit and push - Render will auto-deploy

## Troubleshooting

### "Page not found" error
- Check publish directory is exactly: `frontend/.next`
- Make sure base directory is: `frontend`
- Try "Clear cache and deploy site"

### "Failed to fetch" errors
- Verify `NEXT_PUBLIC_API_URL` environment variable is set
- Make sure backend CORS includes your Netlify URL
- Check backend is running on Render

### Build fails
- Check Node version is 18 in Netlify settings
- View build logs for specific errors
- Make sure all dependencies are in package.json

## Your Live URLs
- **Frontend**: Your Netlify URL
- **Backend**: Your Render URL

Share the Netlify URL with your colleagues!
