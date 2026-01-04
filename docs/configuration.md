# Configuration Guide - Centro Medico Gargano AI Voice Assistant

## Final Phone Number Configuration

### Primary Numbers
- **Main Clinic Number (Primary Inbound)**: `+39 081 7809641`
- **Secondary Number**: `+39 081 18114775`
  - Used for outbound calls
  - Used for call transfers to mobile (out of hours)
  - Can also receive inbound calls

### Internal Extensions (Business Hours)
- **Operator Extension 1**: `**611`
- **Operator Extension 2**: `**612`

### Out of Hours Transfer
- **Mobile Number**: `+39 348 7035744`
- **Transfer Via**: `+39 081 18114775` (Secondary FRITZ!Box number)

## Google Calendar Configuration

### Account Credentials
- **Email**: `u7576349717@gmail.com`
- **Password**: `SegretarIA123`
- **Status**: Account is already configured to see the clinic main calendar appointments (red/busy)

### Calendar Setup
- The account has access to the **main clinic calendar**
- Used for:
  - Reading free/busy status (red/busy appointments)
  - Writing new appointments created by the AI

### OAuth Setup Required
To use Google Calendar API, you need to:
1. Create a Google Cloud Project
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Download credentials JSON file
5. Set `GOOGLE_CREDENTIALS_PATH` in `.env` to point to the credentials file

**Note**: The email/password are provided for reference, but the API requires OAuth2 authentication.

## Environment Variables

Create a `.env` file in the `centro-medico-ai/` directory with the following:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_API_KEY_SID=your_api_key_sid
TWILIO_API_KEY_SECRET=your_api_key_secret

# Phone Numbers
MAIN_PHONE_NUMBER=+390817809641
SECONDARY_PHONE_NUMBER=+3908118114775
OPERATOR_EXTENSION_1=**611
OPERATOR_EXTENSION_2=**612
OUT_OF_HOURS_MOBILE=+393487035744
OUT_OF_HOURS_TRANSFER_NUMBER=+3908118114775

# Google Calendar
GOOGLE_CALENDAR_MAIN_ID=your_calendar_id
GOOGLE_CALENDAR_EMAIL=u7576349717@gmail.com
GOOGLE_CREDENTIALS_PATH=path/to/credentials.json

# Business Rules
OFFICE_NAME=Centro Medico Gargano
OFFICE_TIMEZONE=Europe/Rome
OFFICE_OPEN_DAYS=MON,TUE,WED,THU,FRI
OFFICE_OPEN_TIME=09:00
OFFICE_CLOSE_TIME=19:00
APPOINTMENT_DURATION_MINUTES=60
APPOINTMENT_MIN_DAYS_AHEAD=7

# AI Settings
AI_LANGUAGE=it
AI_EMERGENCY_NUMBER=118

# Server
HOST=0.0.0.0
PORT=8000
```

## Call Flow Summary

### Business Hours (Monday-Friday, 09:00-19:00)
1. AI answers incoming calls to main number (`+39 081 7809641`)
2. AI handles:
   - General clinic information
   - Appointment booking (60 minutes, minimum 7 days ahead)
   - Service inquiries
3. If operator needed:
   - Transfer to internal extension (`**611` or `**612`)

### Out of Office Hours
1. AI still answers calls
2. AI informs caller that clinic is closed
3. AI can:
   - Collect information
   - Offer appointment booking (starting from next available date, ≥7 days ahead)
4. If operator needed:
   - Transfer to mobile (`+39 348 7035744`) via secondary number (`+39 081 18114775`)

### Emergency Handling
- AI never handles emergencies
- Directs caller to **118** (Italian medical emergency service)

## Appointment Booking Rules

1. **Duration**: Always 60 minutes
2. **Minimum Advance**: At least 7 days from call date
3. **Days**: Monday-Friday only (no weekends)
4. **Hours**: 09:00-19:00
5. **Availability**: Checked via Google Calendar (main clinic calendar)
6. **Storage**: Patient name, phone number, visit type stored in calendar event

## Important Notes

1. **Phone Numbers**: This is the final configuration - no changes planned
2. **FRITZ!Box**: Both numbers are configured and operational
3. **Call Diversion**: AI integration must not interfere with existing FRITZ!Box call diversion settings
4. **Calendar**: Account `u7576349717@gmail.com` already has access to main calendar
5. **OAuth**: Google Calendar API requires OAuth2 credentials (not email/password)


