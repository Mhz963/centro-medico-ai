# How the Project Works - Centro Medico Gargano AI Voice Assistant

## 🏗️ System Architecture

```
┌─────────────────┐
│   Caller        │
│  (Phone Call)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FRITZ!Box     │
│  +39 081 7809641│ (Main Number)
└────────┬────────┘
         │
         │ Forwards call to
         ▼
┌─────────────────┐
│     Twilio      │
│  (SIP Service)  │
└────────┬────────┘
         │
         │ Sends webhook to
         ▼
┌─────────────────────────────────────┐
│   Your AI Application               │
│   (This Project)                    │
│                                     │
│   - Receives call via webhook       │
│   - Uses OpenAI for AI responses    │
│   - Uses Google Calendar for        │
│     appointment booking              │
│   - Handles transfers               │
└────────┬────────────────────────────┘
         │
         │ Makes API calls to
         ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     OpenAI      │  │ Google Calendar │  │     Twilio      │
│  (ChatGPT API)  │  │      API        │  │  (Voice/SMS)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 📞 Call Flow

### Step-by-Step Process:

1. **Incoming Call**
   - Someone calls `+39 081 7809641` (main clinic number)
   - FRITZ!Box receives the call

2. **Call Forwarding**
   - FRITZ!Box forwards the call to Twilio (via SIP/webhook)
   - Twilio receives the call and sends webhook to your application

3. **AI Processing**
   - Your application receives the webhook at `/webhook/voice`
   - AI answers: "Buongiorno, Centro Medico Gargano, come posso aiutarla?"
   - Twilio's speech recognition transcribes caller's speech

4. **Conversation**
   - Transcribed text sent to OpenAI (ChatGPT)
   - AI generates response in Italian
   - Response converted to speech via Twilio TTS
   - Caller hears the response

5. **Actions**
   - If appointment booking: AI checks Google Calendar, creates appointment
   - If operator needed: AI transfers to **611/**612 (business hours) or mobile (out of hours)
   - If emergency: AI directs to 118

6. **Call Ends**
   - Either naturally or after transfer

## 🖥️ Do You Need to Run It?

### Option 1: You Run It (Self-Hosted)
**Pros:**
- Full control
- No ongoing cloud costs (after setup)
- Data stays on your server

**Cons:**
- Need a server/computer running 24/7
- Need to maintain it
- Need to handle updates
- Need reliable internet connection
- Need to configure firewall/security

**Requirements:**
- Computer/server running 24/7
- Internet connection
- Python installed
- All environment variables configured

**How to run:**
```bash
python run.py  # Keeps running until you stop it
```

---

### Option 2: Cloud Deployment (Recommended)
**Pros:**
- No need to keep your computer on
- Automatic updates possible
- Professional hosting
- Better reliability
- HTTPS included
- Easy scaling

**Cons:**
- Monthly hosting costs (~$5-20/month)
- Need to configure cloud account

**Recommended Platforms:**
- **Railway.app** - Easiest, ~$5/month
- **Render.com** - Free tier available
- **Heroku** - Popular, easy setup
- **AWS/GCP/Azure** - Enterprise-grade

**How it works:**
1. Deploy code to cloud platform
2. Set environment variables in platform dashboard
3. Platform keeps it running 24/7
4. You get a public URL (e.g., `https://your-app.railway.app`)
5. Configure Twilio webhook to point to this URL
6. Done! No need to run anything yourself

---

## 🔧 What Needs to Be Running?

### For the System to Work:

1. **Your Application** (this project)
   - Must be running 24/7
   - Can be on your computer OR cloud server
   - Must be accessible from internet (for Twilio webhooks)

2. **Twilio Account**
   - Already running (their service)
   - You just need to configure webhook URL

3. **OpenAI API**
   - Already running (their service)
   - You just need API key

4. **Google Calendar API**
   - Already running (their service)
   - You just need OAuth credentials

5. **FRITZ!Box**
   - Already running (your hardware)
   - Just needs call forwarding configured

### What YOU Need to Do:

**If Self-Hosting:**
- Keep your computer/server running
- Run: `python run.py` (or use system service)
- Ensure internet connection is stable
- Monitor for errors

**If Cloud Hosting:**
- Deploy once to cloud platform
- Set environment variables
- Configure Twilio webhook
- That's it! Platform keeps it running

---

## 🚀 Recommended Approach

### For Production Use: **Cloud Deployment**

**Why?**
- More reliable (99.9% uptime)
- No need to keep your computer on
- Automatic HTTPS
- Easy to scale
- Professional setup

**Steps:**
1. Deploy to Railway.app or Render.com (easiest)
2. Set environment variables in their dashboard
3. Get public URL
4. Configure Twilio webhook to point to URL
5. Done! System runs automatically

**Cost:** ~$5-10/month for basic hosting

---

## 📋 Quick Comparison

| Aspect | Self-Hosted | Cloud Hosted |
|--------|------------|--------------|
| **Need to run yourself?** | Yes, 24/7 | No, automatic |
| **Computer must be on?** | Yes | No |
| **Setup complexity** | Medium | Easy |
| **Monthly cost** | $0 (electricity) | $5-20 |
| **Reliability** | Depends on you | 99.9% uptime |
| **Maintenance** | You handle | Platform handles |
| **Best for** | Testing, learning | Production |

---

## 🎯 Summary

**How it works:**
- FRITZ!Box forwards calls → Twilio → Your Application → AI responds
- Your application uses OpenAI and Google Calendar APIs
- Everything happens automatically when a call comes in

**Do you need to run it?**
- **For testing:** Yes, run locally with `python run.py`
- **For production:** No, deploy to cloud (recommended)

**What's always running:**
- Twilio (their service)
- OpenAI (their service)
- Google Calendar (their service)
- Your application (either on your computer or cloud)

**What you control:**
- Where to host your application (your computer or cloud)
- When to deploy/update
- Configuration settings

---

## 💡 Recommendation

**For live production use with real patients:**
→ Deploy to **Railway.app** or **Render.com**
→ Set it up once
→ It runs automatically 24/7
→ No need to keep your computer on
→ Professional and reliable

**For testing/development:**
→ Run locally with `python run.py`
→ Use ngrok for Twilio webhook testing
→ Test everything before deploying

---

**See `FINAL_UPDATE.txt` for detailed deployment instructions.**

