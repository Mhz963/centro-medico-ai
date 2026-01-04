"""Appointment management and calendar integration."""
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
from backend.business_rules import BusinessRules
from backend.calendar_service import CalendarService

logger = logging.getLogger(__name__)

class AppointmentManager:
    """Manages appointment booking."""
    
    def __init__(self):
        self.calendar = CalendarService()
        self.duration_minutes = config.APPOINTMENT_DURATION_MINUTES  # Always 60 minutes
        self.days_ahead = config.APPOINTMENT_MIN_DAYS_AHEAD  # Minimum 7 days ahead
    
    def create_appointment(
        self,
        patient_name: Optional[str],
        patient_phone: str,
        visit_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create appointment in calendar.
        Appointments are always 60 minutes and must be at least 7 days ahead.
        
        Args:
            patient_name: Patient's name
            patient_phone: Patient's phone number
            visit_type: Type of visit
        
        Returns:
            Dictionary with success status and appointment details
        """
        try:
            # Get appointment date (7 days from now - minimum)
            appointment_date = BusinessRules.get_appointment_date()
            
            # Find available time slot starting from 7 days ahead
            # Search up to 30 days ahead if needed
            available_time = None
            search_date = appointment_date
            
            for day_offset in range(30):  # Search up to 30 days ahead
                available_time = self._find_available_slot(search_date)
                if available_time:
                    break
                search_date = search_date + timedelta(days=1)
                # Skip weekends
                while search_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    search_date = search_date + timedelta(days=1)
            
            if not available_time:
                return {
                    "success": False,
                    "error": "No available slots in the next 30 days"
                }
            
            # Create calendar event
            title = f"Visita - {patient_name}" if patient_name else "Visita - Paziente"
            description = f"Paziente: {patient_name or 'Non specificato'}\nTelefono: {patient_phone}\nTipo visita: {visit_type or 'Generica'}\nPrenotato tramite AI Voice Assistant"
            
            event_result = self.calendar.create_event(
                title=title,
                start_time=available_time,
                duration_minutes=self.duration_minutes,
                description=description
            )
            
            if event_result["success"]:
                return {
                    "success": True,
                    "date": available_time.strftime("%d/%m/%Y"),
                    "time": available_time.strftime("%H:%M"),
                    "patient_name": patient_name,
                    "patient_phone": patient_phone
                }
            else:
                return {
                    "success": False,
                    "error": event_result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_available_slot(self, date: datetime) -> Optional[datetime]:
        """
        Find available time slot on given date.
        Appointments are always 60 minutes long.
        """
        try:
            from backend.config import config
        except ImportError:
            from config import config
        
        # Start from office opening time
        start_hour, start_min = map(int, config.OFFICE_OPEN_TIME.split(":"))
        slot_time = date.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
        
        # Check available slots (every hour during office hours)
        # Appointments are 60 minutes, so we check hourly slots
        end_hour, end_min = map(int, config.OFFICE_CLOSE_TIME.split(":"))
        end_time = date.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
        
        # Check calendar for available slots (60-minute slots)
        while slot_time < end_time:
            # Ensure slot doesn't go past closing time
            slot_end = slot_time + timedelta(minutes=self.duration_minutes)
            if slot_end > end_time:
                break
            
            if self.calendar.is_slot_available(slot_time, self.duration_minutes):
                logger.info(f"Found available slot: {slot_time}")
                return slot_time
            slot_time += timedelta(hours=1)  # Next hour slot
        
        logger.info(f"No available slots found on {date.date()}")
        return None
