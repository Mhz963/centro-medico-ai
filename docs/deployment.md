# Deployment Guide

## Railway.app Deployment (Recommended)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Create new project

### Step 2: Deploy from GitHub
1. Connect GitHub repository
2. Railway will auto-detect Python
3. Set start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

### Step 3: Configure Environment Variables
In Railway dashboard, add:
- OPENAI_API_KEY
- SIP_ACCOUNT_SID (Twilio)
- SIP_AUTH_TOKEN (Twilio)
- SIP_PHONE_NUMBER (Twilio)
- GOOGLE_CALENDAR_ID
- GOOGLE_CREDENTIALS_PATH (or use Railway's file storage)
- OPERATOR_PHONE_NUMBER
- All other config from .env.example

### Step 4: Get Production URL
- Railway provides HTTPS URL automatically
- Use this URL for Twilio webhook

## Render.com Deployment

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up
3. Create new Web Service

### Step 2: Deploy
1. Connect GitHub repository
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables
Add all environment variables in Render dashboard

## Local Testing with ngrok

```bash
# Terminal 1: Run application
cd centro-medico-ai
uvicorn backend.app:app --reload

# Terminal 2: Run ngrok
ngrok http 8000

# Use ngrok URL for Twilio webhook
```

## Post-Deployment Checklist

- [ ] Application deployed and running
- [ ] Health check endpoint working (/health)
- [ ] Twilio webhook configured with production URL
- [ ] Environment variables set correctly
- [ ] Google Calendar credentials uploaded
- [ ] Test webhook endpoint receives calls
- [ ] FRITZ!Box forwarding configured
- [ ] Test with real call




