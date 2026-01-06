# ElevenLabs Agent Transfer Configuration

## Overview
This guide explains how to configure ElevenLabs Agent to handle transfers to:
- **Office hours**: Extensions **611 or **612 (FRITZ!Box internal extensions)
- **Outside hours**: Mobile number +39 348 703 5744

## Option 1: Using Twilio Function (Recommended)

### Step 1: Create Twilio Function
1. Go to: https://console.twilio.com → **Functions and Assets** → **Services**
2. Create a new Service (or use existing)
3. Add a new Function named `transfer-handler`
4. Copy the code from `twilio-function-transfer.js`
5. Save and deploy

### Step 2: Get Function URL
1. After deploying, copy the Function URL
2. It will look like: `https://your-service-xxxxx.twil.io/transfer-handler`

### Step 3: Configure ElevenLabs Agent
1. In ElevenLabs Agent dashboard, go to **Actions** or **Integrations**
2. Add a new action for "transfer to operator"
3. Configure it to call the Twilio Function URL
4. When transfer is needed, Agent will call this function
5. Function will check office hours and route accordingly

## Option 2: Direct Transfer in Agent Configuration

### For Office Hours (611/612)
In your ElevenLabs Agent system prompt or knowledge base, include:

```
When the caller requests to speak with an operator during office hours 
(Monday-Friday, 9:00-19:00 Europe/Rome time):
- Transfer to extension **611 or **612
- Format must include asterisks: **611 or **612
- These are FRITZ!Box internal extensions
```

### For Outside Hours (+39 348 703 5744)
```
When the caller requests to speak with an operator outside office hours:
- Transfer to mobile number: +393487035744
- Use full international format
```

### Configure Transfer Action
1. In ElevenLabs Agent settings, find **Actions** or **Call Actions**
2. Create a transfer action that:
   - Checks current time (Europe/Rome timezone)
   - If office hours: Transfer to **611 or **612
   - If outside hours: Transfer to +393487035744

## Option 3: Using Twilio Studio Flow

### Step 1: Create Studio Flow
1. Go to: https://console.twilio.com → **Studio** → **Flows**
2. Create a new Flow
3. Add a **Run Function** widget that calls the transfer function
4. Or add logic to check office hours and route accordingly

### Step 2: Configure ElevenLabs to Route to Studio
1. In ElevenLabs Agent, configure transfer to route to Studio Flow
2. Studio Flow handles the office hours logic and transfer

## Office Hours Logic

**Office Hours:**
- Days: Monday - Friday
- Time: 09:00 - 19:00
- Timezone: Europe/Rome

**Transfer Rules:**
- **During office hours**: Transfer to **611 or **612 (FRITZ!Box extensions)
- **Outside office hours**: Transfer to +39 348 703 5744 (mobile)

## Important Notes

1. **Extension Format**: 
   - Must include asterisks: `**611` or `**612`
   - This is required for FRITZ!Box feature codes
   - Do NOT use `611` or `612` without asterisks

2. **Mobile Number Format**:
   - Use full international format: `+393487035744`
   - No spaces or dashes
   - Include country code (+39)

3. **Timezone**:
   - All time checks must use Europe/Rome timezone
   - Account for daylight saving time automatically

4. **Testing**:
   - Test during office hours (should transfer to **611/**612)
   - Test outside office hours (should transfer to mobile)
   - Verify transfers complete successfully

## Testing Checklist

- [ ] Transfer during office hours routes to **611 or **612
- [ ] Transfer outside office hours routes to +39 348 703 5744
- [ ] Transfer completes successfully
- [ ] No "application error" messages
- [ ] Call connects to operator/extension

