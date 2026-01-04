# Deploy to Render - Step by Step Guide

## Prerequisites
- Render account (sign up at https://render.com - free tier available)
- GitHub account (or GitLab/Bitbucket)
- Your project code ready

## Step 1: Prepare Your Code

### 1.1 Ensure all files are ready
- ✅ All code is in `centro-medico-ai/` directory
- ✅ `requirements.txt` exists
- ✅ `.env.example` exists (for reference)
- ✅ `Procfile` exists (for Render)

### 1.2 Check Procfile
The `Procfile` should contain:
```
web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```

## Step 2: Push to GitHub

### 2.1 Initialize Git (if not already done)
```bash
cd E:\Documents\Cursor\FRITZbox\centro-medico-ai
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

### 2.2 Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., `centro-medico-ai`)
3. **DO NOT** initialize with README (if you have code already)

### 2.3 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/centro-medico-ai.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Render

### 3.1 Create Render Account
1. Go to https://render.com
2. Sign up (use GitHub to connect - easier)
3. Verify your email

### 3.2 Create New Web Service
1. Click **"New +"** button
2. Select **"Web Service"**
3. Connect your GitHub account (if not already connected)
4. Select your repository: `centro-medico-ai`

### 3.3 Configure Service Settings

**Basic Settings:**
- **Name**: `centro-medico-ai` (or any name you prefer)
- **Region**: Choose closest to Italy (e.g., Frankfurt, Europe)
- **Branch**: `main` (or your default branch)
- **Root Directory**: `centro-medico-ai` (important!)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Auto-Deploy**: `Yes` (deploys on every push to main)

### 3.4 Add Environment Variables

Click **"Add Environment Variable"** and add ALL variables from your `.env` file:

**Required Variables:**
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_API_KEY_SID=your_twilio_api_key_sid_here
TWILIO_API_KEY_SECRET=your_twilio_api_key_secret_here
MAIN_PHONE_NUMBER=+390817809641
SECONDARY_PHONE_NUMBER=+3908118114775
OPERATOR_EXTENSION_1=**611
OPERATOR_EXTENSION_2=**612
OUT_OF_HOURS_MOBILE=+393487035744
OUT_OF_HOURS_TRANSFER_NUMBER=+3908118114775
GOOGLE_CALENDAR_MAIN_ID=u7576349717@gmail.com
GOOGLE_CALENDAR_EMAIL=u7576349717@gmail.com
GOOGLE_CREDENTIALS_PATH=./credentials.json
OFFICE_NAME=Centro Medico Gargano
OFFICE_TIMEZONE=Europe/Rome
OFFICE_OPEN_TIME=09:00
OFFICE_CLOSE_TIME=19:00
APPOINTMENT_DURATION_MINUTES=60
APPOINTMENT_MIN_DAYS_AHEAD=7
AI_LANGUAGE=it
AI_EMERGENCY_NUMBER=118
HOST=0.0.0.0
PORT=8000
```

**Note:** For `GOOGLE_CREDENTIALS_PATH`, you'll need to upload the OAuth credentials JSON file separately (see Step 4).

### 3.5 Deploy
1. Click **"Create Web Service"**
2. Render will start building and deploying
3. Wait 3-5 minutes for deployment to complete
4. You'll see build logs in real-time

## Step 4: Upload Google Calendar Credentials

### 4.1 After Deployment
1. Go to your service dashboard on Render
2. Click **"Environment"** tab
3. For `GOOGLE_CREDENTIALS_PATH`, you have two options:

**Option A: Use Render's File System (Temporary)**
- Upload credentials.json via Render's file system
- Set path accordingly

**Option B: Use Environment Variable (Recommended)**
- Convert credentials.json to base64
- Store as environment variable
- Or use a secrets manager

**For now:** You can set `GOOGLE_CREDENTIALS_PATH` to empty and handle OAuth setup later.

## Step 5: Get Your Public URL

### 5.1 After Successful Deployment
1. Render will provide a URL like: `https://centro-medico-ai.onrender.com`
2. Copy this URL - you'll need it for Twilio webhook

### 5.2 Test Your Deployment
```bash
# Test health endpoint
curl https://your-app.onrender.com/health

# Should return: {"status":"healthy"}
```

## Step 6: Configure Twilio Webhook

### 6.1 In Twilio Console
1. Go to https://console.twilio.com
2. Navigate to **Phone Numbers** > **Manage** > **Active Numbers**
3. Select your Twilio number
4. In **Voice & Fax** section:
   - **A CALL COMES IN**: Webhook
   - **URL**: `https://your-app.onrender.com/webhook/voice`
   - **HTTP**: POST
5. Click **Save**

## Step 7: Verify Deployment

### 7.1 Test Endpoints
- Health: `https://your-app.onrender.com/health`
- Root: `https://your-app.onrender.com/`
- Webhook (GET): `https://your-app.onrender.com/webhook/voice`

### 7.2 Check Logs
- Go to Render dashboard
- Click **"Logs"** tab
- Monitor for any errors

## Step 8: Update FRITZ!Box

### 8.1 Configure Call Forwarding
- Forward main number (+39 081 7809641) to Twilio number
- Use the call forwarding interface we saw earlier

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Check Python version compatibility

### Application Crashes
- Check logs for errors
- Verify all environment variables are set
- Check if port is correctly set to `$PORT`

### Webhook Not Working
- Verify URL is correct in Twilio
- Check Render logs for incoming requests
- Ensure HTTPS is used (Render provides this automatically)

## Important Notes

1. **Free Tier Limitations:**
   - Render free tier spins down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds
   - Consider paid plan for production ($7/month)

2. **Environment Variables:**
   - Never commit `.env` file to GitHub
   - All secrets should be in Render's environment variables

3. **Auto-Deploy:**
   - Every push to main branch auto-deploys
   - Use feature branches for testing

4. **Custom Domain:**
   - Render allows custom domains (paid feature)
   - Or use the provided `.onrender.com` domain

## Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] All environment variables added
- [ ] Deployment successful
- [ ] Health endpoint working
- [ ] Twilio webhook configured
- [ ] FRITZ!Box forwarding configured
- [ ] Test call made successfully

## Support

If you encounter issues:
1. Check Render logs
2. Verify environment variables
3. Test endpoints manually
4. Check Twilio webhook logs

---

**Your application will be live at:** `https://your-app-name.onrender.com`

