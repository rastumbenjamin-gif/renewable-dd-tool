# Deploy Backend on Hugging Face Spaces (100% FREE)

Hugging Face Spaces is perfect for ML applications and handles PyTorch without issues.

## Step 1: Create Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up (free account)
3. Verify your email

## Step 2: Create a New Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Settings:
   - **Name**: `renewable-dd-backend`
   - **License**: MIT
   - **Space SDK**: Select **Docker**
   - **Visibility**: Private (recommended)
4. Click "Create Space"

## Step 3: Prepare Dockerfile
I'll create a Dockerfile for you that works with Hugging Face.

## Step 4: Push Code to Space
Hugging Face Spaces work like Git repositories:

```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/renewable-dd-backend
cd renewable-dd-backend

# Copy backend files
cp -r /path/to/renewable-dd-tool/backend/* .

# Add Dockerfile and requirements
git add .
git commit -m "Initial backend deployment"
git push
```

## Step 5: Configure Secrets
1. Go to your Space → Settings → Repository secrets
2. Add secret:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
3. Save

## Step 6: Get Your Backend URL
Your backend will be at:
`https://YOUR_USERNAME-renewable-dd-backend.hf.space`

## Step 7: Update Netlify Frontend
Add environment variable in Netlify:
- Key: `NEXT_PUBLIC_API_URL`
- Value: `https://YOUR_USERNAME-renewable-dd-backend.hf.space`

## Why Hugging Face Spaces?
- ✅ 100% FREE forever
- ✅ Handles PyTorch and large ML libraries
- ✅ No credit card required
- ✅ Designed for ML applications
- ✅ Automatic HTTPS
- ✅ No sleep/downtime
- ✅ Great for demo/portfolio projects
