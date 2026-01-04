"""Twilio client using API Key authentication."""
import logging
import sys
import os
from twilio.rest import Client

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.config import config

logger = logging.getLogger(__name__)

class TwilioClient:
    """Twilio client with API Key authentication."""
    
    def __init__(self):
        """Initialize Twilio client with API Key."""
        try:
            # Use API Key instead of Auth Token
            self.client = Client(
                username=config.TWILIO_API_KEY_SID,
                password=config.TWILIO_API_KEY_SECRET,
                account_sid=config.TWILIO_ACCOUNT_SID
            )
            logger.info("Twilio client initialized with API Key")
        except Exception as e:
            logger.error(f"Error initializing Twilio client: {e}")
            self.client = None
    
    def get_client(self):
        """Get Twilio client instance."""
        return self.client

# Global instance
twilio_client = TwilioClient()




