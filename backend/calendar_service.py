"""Google Calendar integration service."""
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.config import config

logger = logging.getLogger(__name__)

class CalendarService:
    """Google Calendar service."""
    
    def __init__(self):
        # Main clinic calendar (read free/busy and write appointments)
        # The account u7576349717@gmail.com is configured to see the clinic main calendar
        self.calendar_main_id = config.GOOGLE_CALENDAR_MAIN_ID
        self.credentials_path = config.GOOGLE_CREDENTIALS_PATH
        self.google_email = config.GOOGLE_CALENDAR_EMAIL  # u7576349717@gmail.com
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar API service."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import pickle
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            creds = None
            token_path = 'token.pickle'
            
            # Load existing token
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        logger.warning("Google Calendar credentials not found. Calendar features will be disabled.")
                        return
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Google Calendar service: {e}")
            self.service = None
    
    def create_event(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create calendar event in main clinic calendar.
        
        Args:
            title: Event title
            start_time: Start datetime
            duration_minutes: Duration in minutes
            description: Event description
        
        Returns:
            Dictionary with success status
        """
        if not self.service:
            return {
                "success": False,
                "error": "Calendar service not initialized"
            }
        
        if not self.calendar_main_id:
            return {
                "success": False,
                "error": "Main calendar ID not configured"
            }
        
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Europe/Rome',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Europe/Rome',
                },
            }
            
            # Write to main clinic calendar
            event = self.service.events().insert(
                calendarId=self.calendar_main_id,
                body=event
            ).execute()
            
            logger.info(f"Event created in main calendar: {event.get('htmlLink')}")
            
            return {
                "success": True,
                "event_id": event.get('id')
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_slot_available(self, start_time: datetime, duration_minutes: int) -> bool:
        """
        Check if time slot is available by reading free/busy from main calendar.
        The account is configured to see the clinic main calendar appointments (red/busy).
        
        Args:
            start_time: Start datetime
            duration_minutes: Duration in minutes
        
        Returns:
            True if slot is available
        """
        if not self.service:
            logger.warning("Calendar service not initialized, assuming slot is available")
            return True  # Assume available if calendar not configured
        
        if not self.calendar_main_id:
            logger.warning("Main calendar ID not configured, assuming slot is available")
            return True
        
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Check main calendar for existing appointments (red/busy)
            # The account u7576349717@gmail.com can see the clinic main calendar
            events_result = self.service.events().list(
                calendarId=self.calendar_main_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
                
            main_events = events_result.get('items', [])
            if len(main_events) > 0:
                logger.info(f"Slot busy in main calendar at {start_time}: {len(main_events)} event(s) found")
                return False
            
            logger.debug(f"Slot available at {start_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error checking slot availability: {e}")
            # On error, assume available to avoid blocking appointments
            # But log the error for debugging
            return True

