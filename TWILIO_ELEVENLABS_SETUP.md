# Twilio + ElevenLabs Agent Configuration Guide

## Overview
This guide configures Twilio to route calls directly to ElevenLabs Agent via SIP Trunk, removing the Render/webhook flow from the call path.

## Architecture Change

**Old Flow (Webhook-based):**
```
FRITZ!Box → Twilio → Webhook → Render App → TwiML Response
```

**New Flow (SIP Trunk to ElevenLabs):**
```
FRITZ!Box → Twilio → SIP Trunk → ElevenLabs Agent → AI Conversation
```

## Step 1: Configure Twilio Phone Number for SIP Trunk Routing

### 1.1 Access Twilio Console
1. Go to: https://console.twilio.com
2. Navigate to: **Phone Numbers** → **Manage** → **Active Numbers**
3. Click on your Twilio phone number (e.g., `+39800826561`)

### 1.2 Configure Voice Settings
1. Go to the **Voice Configuration** section
2. Under **"A CALL COMES IN"**, change from **"Webhook"** to **"SIP Trunk"**
3. Select your SIP Trunk (or create one if needed)
4. **IMPORTANT**: Remove any webhook URL that points to Render
5. Set the routing to point to your ElevenLabs Agent SIP endpoint

### 1.3 Get ElevenLabs Agent SIP Endpoint
1. In ElevenLabs dashboard, go to your Agent settings
2. Find the **SIP Endpoint** or **SIP URI** for your agent
3. It should look like: `sip:agent-name@elevenlabs.io` or similar
4. Copy this endpoint - you'll need it for Twilio configuration

### 1.4 Configure SIP Trunk in Twilio
1. In Twilio Console, go to: **Elastic SIP Trunking** → **Trunks**
2. If you don't have a trunk, create one:
   - Click **"Create Trunk"**
   - Name it (e.g., "ElevenLabs Agent Trunk")
3. Add the ElevenLabs SIP endpoint as a **Credential List** or **IP Access Control List**
4. Configure the trunk to route to ElevenLabs Agent SIP endpoint

## Step 2: Verify Audio Streaming

### 2.1 Test Call Flow
1. Make a test call to your Twilio number
2. Verify that:
   - Call connects (no "application error")
   - Audio streams to ElevenLabs Agent
   - AI responds in Italian
   - No disconnections

### 2.2 Check Twilio Logs
1. Go to: **Monitor** → **Logs** → **Calls**
2. Check recent calls for:
   - Status: "completed" (not "failed")
   - No error messages
   - SIP connection established

### 2.3 Check ElevenLabs Dashboard
1. In ElevenLabs Agent dashboard, check:
   - Incoming calls are being received
   - Audio is streaming correctly
   - Agent is responding

## Step 3: Configure Transfers in ElevenLabs Agent

### 3.1 Office Hours Transfers (611 / 612)
The ElevenLabs Agent needs to be configured to transfer calls to FRITZ!Box extensions during office hours.

**Transfer Format:**
- Extension **611**: Use `**611` (with asterisks)
- Extension **612**: Use `**612` (with asterisks)

**Configuration in ElevenLabs:**
1. In your Agent's system prompt or knowledge base, include:
   ```
   When transferring to operator during office hours (Monday-Friday, 9:00-19:00):
   - Use extension **611 or **612
   - Format: **611 or **612 (include asterisks)
   ```

2. Configure the Agent's transfer action to use Twilio's Dial verb with the extension format

### 3.2 Outside Office Hours Transfers (+39 348 703 5744)
For calls outside office hours, transfer to the mobile number.

**Mobile Number:** `+39 348 703 5744`

**Configuration:**
1. In Agent settings, configure transfer action for outside hours
2. Use full international format: `+393487035744` (no spaces)

### 3.3 Transfer Implementation Options

**Option A: Via Twilio Functions (Recommended)**
1. Create a Twilio Function that handles transfers
2. Configure ElevenLabs Agent to call this function when transfer is needed
3. Function checks office hours and routes accordingly:
   - Office hours → `**611` or `**612`
   - Outside hours → `+393487035744`

**Option B: Via ElevenLabs Agent Actions**
1. Configure Agent actions in ElevenLabs dashboard
2. Set up transfer actions that call Twilio API
3. Use Twilio REST API to initiate transfers

**Option C: Via Twilio Studio Flow**
1. Create a Studio Flow that handles the transfer logic
2. Route calls: ElevenLabs Agent → Studio Flow → Transfer
3. Studio Flow checks office hours and transfers accordingly

## Step 4: Remove Render/Webhook Configuration

### 4.1 Remove Webhook from Twilio
1. In Twilio Console → Phone Numbers → Your Number
2. Under **Voice Configuration** → **"A CALL COMES IN"**
3. **Remove** or **clear** any webhook URL pointing to:
   - `https://centro-medico-ai.onrender.com/webhook/voice`
   - Any other Render/webhook URLs
4. Set to **"SIP Trunk"** instead

### 4.2 Verify No Webhook Fallbacks
1. Check **"Primary handler fails"** section
2. Remove any webhook URLs there as well
3. Ensure all routing goes through SIP Trunk

## Step 5: Office Hours Detection

### 5.1 Current Office Hours Configuration
- **Days**: Monday-Friday (MON, TUE, WED, THU, FRI)
- **Time**: 09:00 - 19:00 (Europe/Rome timezone)
- **Outside Hours**: All other times

### 5.2 Implementation in Transfer Logic
When implementing transfers (via Twilio Function or Studio Flow), use this logic:

```javascript
// Pseudo-code for office hours check
const now = new Date();
const timezone = 'Europe/Rome';
const hour = now.getHours();
const day = now.getDay(); // 0=Sunday, 1=Monday, etc.

const isOfficeHours = 
  day >= 1 && day <= 5 && // Monday-Friday
  hour >= 9 && hour < 19; // 9:00-19:00

if (isOfficeHours) {
  // Transfer to **611 or **612
  transferTo = '**611'; // or **612
} else {
  // Transfer to mobile
  transferTo = '+393487035744';
}
```

## Step 6: Testing Checklist

### 6.1 Basic Call Flow
- [ ] Call connects without "application error"
- [ ] Audio streams to ElevenLabs Agent
- [ ] AI responds in Italian
- [ ] Conversation flows naturally
- [ ] No disconnections

### 6.2 Office Hours Transfer (611/612)
- [ ] During office hours (Mon-Fri, 9:00-19:00)
- [ ] Request operator transfer
- [ ] Call transfers to extension **611 or **612
- [ ] Transfer completes successfully

### 6.3 Outside Hours Transfer (+39 348 703 5744)
- [ ] Outside office hours
- [ ] Request operator transfer
- [ ] Call transfers to mobile number +39 348 703 5744
- [ ] Transfer completes successfully

### 6.4 Appointment Booking
- [ ] AI can understand appointment requests
- [ ] Appointments are saved (if Google Calendar is configured)
- [ ] Confirmation is provided to caller

## Step 7: Troubleshooting

### Issue: "Application error" still occurs
**Solution:**
- Verify webhook URL is completely removed from Twilio phone number
- Check that SIP Trunk routing is active
- Verify ElevenLabs Agent SIP endpoint is correct
- Check Twilio logs for SIP connection errors

### Issue: Audio not streaming to ElevenLabs
**Solution:**
- Verify SIP Trunk is properly configured
- Check ElevenLabs Agent SIP endpoint is accessible
- Verify codec compatibility (G.711 recommended)
- Check network/firewall settings

### Issue: Transfers not working
**Solution:**
- Verify transfer format: `**611` or `**612` (with asterisks)
- Check office hours detection logic
- Verify mobile number format: `+393487035744`
- Test transfer action in ElevenLabs Agent settings

### Issue: Calls disconnect after 2 rings
**Solution:**
- Check SIP Trunk configuration
- Verify ElevenLabs Agent is active and published
- Check Twilio call logs for error messages
- Verify SIP credentials are correct

## Important Notes

1. **Render App is No Longer in Call Path**
   - The Render webhook endpoints are not used for incoming calls
   - The app can remain deployed for other purposes (if needed)
   - But it's not part of the call routing anymore

2. **ElevenLabs Agent Handles Everything**
   - AI conversation
   - Speech recognition
   - Text-to-speech
   - Natural language understanding

3. **Transfers Must Be Configured in ElevenLabs or Twilio**
   - Either via ElevenLabs Agent actions
   - Or via Twilio Functions/Studio Flow
   - Not via the Render app anymore

4. **Office Hours Logic**
   - Must be implemented in the transfer mechanism
   - Either in ElevenLabs Agent configuration
   - Or in Twilio Function/Studio Flow

## Next Steps

1. ✅ Configure Twilio phone number for SIP Trunk routing
2. ✅ Verify audio streaming to ElevenLabs Agent
3. ✅ Configure transfers (611/612 or mobile)
4. ✅ Test end-to-end call flow
5. ✅ Verify office hours detection works
6. ✅ Test transfers in both scenarios

---

**Once this is configured, the Render/webhook flow is completely removed from the call path, and all calls go directly from Twilio to ElevenLabs Agent via SIP Trunk.**

