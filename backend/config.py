"""Configuration management for the application."""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Application configuration."""
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Default fallback
    
    # Twilio (API Key based, not Auth Token)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_API_KEY_SID: str = os.getenv("TWILIO_API_KEY_SID", "")
    TWILIO_API_KEY_SECRET: str = os.getenv("TWILIO_API_KEY_SECRET", "")
    # Main clinic number (primary inbound number)
    MAIN_PHONE_NUMBER: str = os.getenv("MAIN_PHONE_NUMBER", "+390817809641")
    # Secondary number (for outbound calls and transfers)
    SECONDARY_PHONE_NUMBER: str = os.getenv("SECONDARY_PHONE_NUMBER", "+3908118114775")
    # Internal operator extensions (during business hours)
    # These are FRITZ!Box internal extensions, use format: **611 or **612
    OPERATOR_EXTENSION_1: str = os.getenv("OPERATOR_EXTENSION_1", "**611")
    OPERATOR_EXTENSION_2: str = os.getenv("OPERATOR_EXTENSION_2", "**612")
    
    # Google Calendar
    # AI calendar for writing appointments
    GOOGLE_CALENDAR_AI_ID: str = os.getenv("GOOGLE_CALENDAR_AI_ID", "")
    # Main clinic calendar (read free/busy, red/busy status)
    GOOGLE_CALENDAR_MAIN_ID: str = os.getenv("GOOGLE_CALENDAR_MAIN_ID", "")
    # Google account credentials (u7576349717@gmail.com / SegretarIA123)
    GOOGLE_CALENDAR_EMAIL: str = os.getenv("GOOGLE_CALENDAR_EMAIL", "u7576349717@gmail.com")
    GOOGLE_CALENDAR_PASSWORD: str = os.getenv("GOOGLE_CALENDAR_PASSWORD", "SegretarIA123")
    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "")
    
    # Business Rules
    OFFICE_NAME: str = os.getenv("OFFICE_NAME", "Centro Medico Gargano")
    OFFICE_TIMEZONE: str = os.getenv("OFFICE_TIMEZONE", "Europe/Rome")
    OFFICE_OPEN_DAYS: str = os.getenv("OFFICE_OPEN_DAYS", "MON,TUE,WED,THU,FRI")
    OFFICE_OPEN_TIME: str = os.getenv("OFFICE_OPEN_TIME", "09:00")
    OFFICE_CLOSE_TIME: str = os.getenv("OFFICE_CLOSE_TIME", "19:00")
    # Appointment settings
    APPOINTMENT_DURATION_MINUTES: int = int(os.getenv("APPOINTMENT_DURATION_MINUTES", "60"))  # Always 60 minutes
    APPOINTMENT_MIN_DAYS_AHEAD: int = int(os.getenv("APPOINTMENT_MIN_DAYS_AHEAD", "7"))  # Minimum 7 days ahead
    
    # AI Behaviour
    AI_LANGUAGE: str = os.getenv("AI_LANGUAGE", "it")
    AI_FALLBACK_ENABLED: bool = os.getenv("AI_FALLBACK_ENABLED", "true").lower() == "true"
    AI_EMERGENCY_NUMBER: str = os.getenv("AI_EMERGENCY_NUMBER", "118")
    
    # Out of Hours Transfer
    # Mobile number for out-of-hours transfers
    OUT_OF_HOURS_MOBILE: str = os.getenv("OUT_OF_HOURS_MOBILE", "+393487035744")
    # Secondary FRITZ!Box number used for outbound transfers to mobile
    OUT_OF_HOURS_TRANSFER_NUMBER: str = os.getenv("OUT_OF_HOURS_TRANSFER_NUMBER", "+3908118114775")
    
    # Logging / Safety
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    STORE_CALL_AUDIO: bool = os.getenv("STORE_CALL_AUDIO", "false").lower() == "true"
    STORE_TRANSCRIPTS: bool = os.getenv("STORE_TRANSCRIPTS", "false").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Legacy support (for backward compatibility)
    @property
    def PHONE_NUMBER(self) -> str:
        """Legacy: Current main phone number."""
        return self.MAIN_PHONE_NUMBER
    
    @property
    def OPERATOR_PHONE_NUMBER(self) -> str:
        """Legacy: Operator phone number (internal extension)."""
        return self.OPERATOR_EXTENSION_1
    
    @property
    def OPERATOR_EXTENSIONS(self) -> list:
        """Get list of operator extensions."""
        return [self.OPERATOR_EXTENSION_1, self.OPERATOR_EXTENSION_2]
    
    @property
    def SIP_ACCOUNT_SID(self) -> str:
        """Legacy: Twilio Account SID."""
        return self.TWILIO_ACCOUNT_SID
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required = [
            cls.OPENAI_API_KEY,
            cls.TWILIO_ACCOUNT_SID,
            cls.TWILIO_API_KEY_SID,
            cls.TWILIO_API_KEY_SECRET,
        ]
        return all(required)

config = Config()

