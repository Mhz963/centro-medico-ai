# Render Deployment Troubleshooting

## Common Runtime Errors After Successful Build

### 1. Module Import Errors
**Error:** `ModuleNotFoundError: No module named 'config'` or similar

**Solution:** ✅ Fixed - All imports now use proper path setup

### 2. Missing Environment Variables
**Error:** Application starts but services fail

**Check:**
- Go to Render Dashboard → Your Service → Environment
- Verify all variables from `dummyenv.env` are set
- Ensure no typos in variable names
- Check that values are correct (no extra spaces)

**Required Variables:**
- `OPENAI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_API_KEY_SID`
- `TWILIO_API_KEY_SECRET`
- `MAIN_PHONE_NUMBER`
- `SECONDARY_PHONE_NUMBER`
- All other variables from `dummyenv.env`

### 3. Port Binding Issues
**Error:** `Address already in use` or port errors

**Solution:** 
- Render automatically sets `$PORT` environment variable
- The `Procfile` uses `--port $PORT` which is correct
- No action needed

### 4. Service Initialization Errors
**Error:** `Failed to initialize CallHandler` or similar

**Possible Causes:**
- Missing OpenAI API key
- Missing Twilio credentials
- Google Calendar credentials issue (non-critical)

**Check Logs:**
- Go to Render Dashboard → Your Service → Logs
- Look for initialization errors
- Check which service is failing

### 5. Application Crashes on Startup
**Error:** Application exits immediately after starting

**Debug Steps:**
1. Check Render logs for error messages
2. Verify all environment variables are set
3. Test locally first: `python run.py`
4. Check if Python version matches `runtime.txt` (3.12.7)

### 6. Health Check Failing
**Error:** Health endpoint returns 500 or doesn't respond

**Test:**
```bash
curl https://your-app.onrender.com/health
```

**Should return:**
```json
{"status": "healthy"}
```

**If it fails:**
- Check application logs
- Verify application started successfully
- Check for import errors

### 7. Google Calendar Warnings
**Warning:** `Google Calendar credentials not found`

**Status:** ✅ This is expected and non-critical
- Application will work without calendar
- Calendar features will be disabled
- Can be configured later with OAuth

### 8. Twilio Webhook Not Working
**Error:** Calls don't reach the application

**Check:**
1. Verify webhook URL in Twilio: `https://your-app.onrender.com/webhook/voice`
2. Ensure URL uses HTTPS (Render provides this automatically)
3. Check Render logs for incoming requests
4. Verify Twilio number is configured correctly

## How to Check Logs

1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Look for:
   - `Application starting up...`
   - `Call handler initialized successfully`
   - `All critical environment variables are set`
   - `Application ready to handle calls`

## Quick Health Check

1. **Health Endpoint:**
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **Root Endpoint:**
   ```bash
   curl https://your-app.onrender.com/
   ```

3. **Webhook Endpoint (GET):**
   ```bash
   curl https://your-app.onrender.com/webhook/voice
   ```

## Common Error Messages and Solutions

### "Failed to initialize CallHandler"
- Check if OpenAI API key is set
- Check if Twilio credentials are set
- Look for specific error in logs

### "ModuleNotFoundError"
- ✅ Should be fixed with latest changes
- If persists, check that all files were committed and pushed

### "Application exited with code 1"
- Check full error in logs
- Usually indicates missing environment variable or import error

### "Service unavailable" when calling
- Check if application is running (not spun down on free tier)
- Free tier spins down after 15 min inactivity
- First request after spin-down takes ~30 seconds

## Next Steps After Deployment

1. ✅ Verify health endpoint works
2. ✅ Check logs for initialization success
3. ✅ Configure Twilio webhook URL
4. ✅ Test with a call
5. ✅ Monitor logs during first call

## Getting Help

If errors persist:
1. Copy full error message from Render logs
2. Check which service is failing
3. Verify environment variables
4. Test locally first to isolate issue

