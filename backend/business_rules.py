"""Business rules for Centro Medico Gargano."""
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pytz

class BusinessRules:
    """Business rules and logic."""
    
    @staticmethod
    def get_office_timezone():
        """Get office timezone from config."""
        try:
            from backend.config import config
            return pytz.timezone(config.OFFICE_TIMEZONE)
        except (ImportError, AttributeError):
            return pytz.timezone("Europe/Rome")
    
    @staticmethod
    def get_office_hours():
        """Get office hours from config."""
        try:
            from backend.config import config
            return config.OFFICE_OPEN_TIME, config.OFFICE_CLOSE_TIME
        except (ImportError, AttributeError):
            return "09:00", "19:00"
    
    @staticmethod
    def is_office_hours() -> Tuple[bool, Optional[str], bool]:
        """
        Check if current time is within office hours.
        Returns: (is_open, next_opening_message, should_transfer_out_of_hours)
        """
        try:
            from backend.config import config
        except ImportError:
            from config import config
        
        now = datetime.now(BusinessRules.get_office_timezone())
        current_time = now.time()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Parse office hours from config
        start_hour, start_min = map(int, config.OFFICE_OPEN_TIME.split(":"))
        end_hour, end_min = map(int, config.OFFICE_CLOSE_TIME.split(":"))
        
        start_time = datetime.now().replace(hour=start_hour, minute=start_min).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_min).time()
        
        # Check if weekend
        if current_weekday >= 5:  # Saturday or Sunday
            # Find next Monday
            days_until_monday = (7 - current_weekday) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_open = now + timedelta(days=days_until_monday)
            next_open = next_open.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
            return False, f"Lunedì alle {config.OFFICE_OPEN_TIME}", True  # Transfer out of hours
        
        # Check if within office hours
        if start_time <= current_time < end_time:
            return True, None, False
        
        # Outside hours on weekday
        if current_time < start_time:
            # Same day, opens later
            return False, f"oggi alle {config.OFFICE_OPEN_TIME}", True  # Transfer out of hours
        else:
            # After hours, next day
            next_open = now + timedelta(days=1)
            if next_open.weekday() >= 5:  # If next day is weekend, go to Monday
                days_until_monday = (7 - next_open.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 7
                next_open = next_open + timedelta(days=days_until_monday)
            next_msg = f"domani alle {config.OFFICE_OPEN_TIME}" if next_open.date() == (now + timedelta(days=1)).date() else f"Lunedì alle {config.OFFICE_OPEN_TIME}"
            return False, next_msg, True  # Transfer out of hours
    
    @staticmethod
    def get_appointment_date() -> datetime:
        """
        Get the appointment date (minimum 7 business days from now).
        Skips weekends to ensure appointments are only on weekdays.
        """
        try:
            from backend.config import config
            days_ahead = config.APPOINTMENT_MIN_DAYS_AHEAD
        except (ImportError, AttributeError):
            days_ahead = 7
        
        now = datetime.now(BusinessRules.get_office_timezone())
        appointment_date = now + timedelta(days=days_ahead)
        
        # Skip weekends - ensure appointment is on a weekday (Mon-Fri)
        while appointment_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            appointment_date = appointment_date + timedelta(days=1)
        
        return appointment_date
    
    @staticmethod
    def is_emergency(text: str) -> bool:
        """Check if text contains emergency keywords."""
        emergency_keywords = [
            "emergenza", "emergenze", "dolore acuto", 
            "urgente", "pronto soccorso", "118"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)
    
    @staticmethod
    def get_emergency_response() -> str:
        """Get standard emergency response."""
        try:
            from backend.config import config
            emergency_num = config.AI_EMERGENCY_NUMBER
        except (ImportError, AttributeError):
            emergency_num = "118"
        
        return f"Per le emergenze mediche le consiglio di contattare immediatamente il {emergency_num} o di recarsi al pronto soccorso più vicino."

