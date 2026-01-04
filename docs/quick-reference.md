# Quick Reference - Centro Medico Gargano AI Voice Assistant

## Phone Numbers (FINAL - DO NOT CHANGE)

- **Main Number**: `+39 081 7809641` (primary inbound)
- **Secondary Number**: `+39 081 18114775` (outbound, transfers)

## Operator Transfers

### Business Hours (Mon-Fri, 09:00-19:00)
- **Internal Extensions**: `**611` or `**612`

### Out of Hours
- **Mobile**: `+39 348 7035744`
- **Via**: `+39 081 18114775` (secondary FRITZ!Box number)

## Google Calendar

- **Account**: `u7576349717@gmail.com`
- **Password**: `SegretarIA123`
- **Status**: Configured to see clinic main calendar (red/busy)
- **Note**: Requires OAuth2 credentials JSON file for API access

## Appointment Rules

- **Duration**: 60 minutes (always)
- **Minimum Advance**: 7 days from call date
- **Days**: Monday-Friday only
- **Hours**: 09:00-19:00

## Emergency

- **Number**: 118 (Italian medical emergency)
- AI never handles emergencies - always directs to 118

## Business Hours

- **Days**: Monday-Friday
- **Time**: 09:00-19:00
- **Timezone**: Europe/Rome

## Key Files

- Configuration: `backend/config.py`
- Call Handler: `backend/call_handler.py`
- Calendar: `backend/calendar_service.py`
- Appointments: `backend/appointment_manager.py`
- Transfer: `backend/operator_transfer.py`

## Environment Setup

1. Copy `.env.example` to `.env`
2. Fill in all values
3. Set up Google Calendar OAuth
4. Configure Twilio webhook
5. Deploy

## Documentation

- Full config: `CONFIGURATION_GUIDE.md`
- Update summary: `PROJECT_UPDATE_SUMMARY.md`
- Completion: `milestone2/PROJECT_COMPLETION_SUMMARY.md`


