"""Call handling and orchestration."""
import logging
import sys
import os
from typing import Dict, Any, Optional

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.config import config
from backend.chatgpt_service import ChatGPTService
from backend.stt_service import STTService
from backend.tts_service import TTSService
from backend.appointment_manager import AppointmentManager
from backend.business_rules import BusinessRules

logger = logging.getLogger(__name__)

class CallHandler:
    """Handles incoming calls and orchestrates conversation."""
    
    def __init__(self):
        try:
            self.chatgpt = ChatGPTService()
            self.stt = STTService()
            self.tts = TTSService()
            self.appointment_manager = AppointmentManager()
            self.conversation_context: Dict[str, Any] = {}
            logger.info("CallHandler initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CallHandler: {e}")
            raise
    
    def handle_call(self, call_sid: str, from_number: str) -> Dict[str, Any]:
        """Handle incoming call."""
        logger.info(f"Handling call {call_sid} from {from_number}")
        
        # Check office hours
        office_result = BusinessRules.is_office_hours()
        is_open = office_result[0]
        next_opening = office_result[1] if len(office_result) > 1 else None
        should_transfer = office_result[2] if len(office_result) > 2 else False
        
        if not is_open:
            # Out of hours: Inform caller and set context
            # Store out_of_hours flag in context for later use
            self.conversation_context[call_sid] = {
                "from_number": from_number,
                "history": [],
                "appointment_booking": False,
                "out_of_hours": True
            }
            return {
                "action": "say",
                "text": f"Il centro è attualmente chiuso. Il prossimo orario di apertura è {next_opening}. Posso aiutarla a prenotare un appuntamento per il primo giorno utile, oppure se ha bisogno di un operatore posso trasferirla.",
                "transfer": False,
                "out_of_hours": True,
                "should_transfer_if_operator_needed": should_transfer
            }
        
        # Initialize conversation (business hours)
        self.conversation_context[call_sid] = {
            "from_number": from_number,
            "history": [],
            "appointment_booking": False,
            "out_of_hours": False  # Business hours
        }
        
        # Return greeting
        return {
            "action": "say",
            "text": "Buongiorno, Centro Medico Gargano, come posso aiutarla?",
            "transfer": False
        }
    
    def process_speech(self, call_sid: str, audio_data: bytes) -> Dict[str, Any]:
        """Process speech input from caller (audio bytes)."""
        try:
            # Transcribe speech
            transcript = self.stt.transcribe(audio_data)
            logger.info(f"Call {call_sid}: Transcript - {transcript}")
            
            if not transcript:
                return {
                    "action": "say",
                    "text": "Non ho capito, può ripetere?",
                    "transfer": False,
                    "end_call": False
                }
            
            return self.process_speech_text(call_sid, transcript)
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}", exc_info=True)
            return {
                "action": "say",
                "text": "Mi dispiace, non ho capito. Può ripetere?",
                "transfer": False,
                "end_call": False
            }
    
    def process_speech_text(self, call_sid: str, transcript: str) -> Dict[str, Any]:
        """Process transcribed text from caller."""
        try:
            if not transcript:
                return {
                    "action": "say",
                    "text": "Non ho capito, può ripetere?",
                    "transfer": False,
                    "end_call": False
                }
            
            logger.info(f"Call {call_sid}: Processing transcript - {transcript}")
            
            # Check for emergency
            if BusinessRules.is_emergency(transcript):
                return {
                    "action": "say",
                    "text": BusinessRules.get_emergency_response(),
                    "transfer": False,
                    "end_call": False
                }
            
            # Get context
            context = self.conversation_context.get(call_sid, {})
            history = context.get("history", [])
            
            # Process with ChatGPT
            response = self.chatgpt.get_response(
                user_message=transcript,
                conversation_history=history
            )
            
            # Update history
            history.append({"role": "user", "content": transcript})
            history.append({"role": "assistant", "content": response["text"]})
            context["history"] = history
            self.conversation_context[call_sid] = context
            
            # Check if transfer needed
            if response.get("transfer_to_operator", False):
                # Check if out of hours
                office_result = BusinessRules.is_office_hours()
                is_open = office_result[0]
                
                if not is_open:
                    # Out of hours: transfer to mobile using secondary FRITZ!Box number
                    transfer_to = config.OUT_OF_HOURS_MOBILE
                    transfer_number = config.OUT_OF_HOURS_TRANSFER_NUMBER
                    is_internal = False
                    extension = None
                    transfer_text = (
                        "Centro Medico Gargano è attualmente chiuso, "
                        "ma la metto in contatto con l’operatore reperibile."
                    )
                    logger.info(f"Out of hours transfer: Using {transfer_number} to reach {transfer_to}")
                else:
                    # Business hours: transfer to internal extension
                    # Use first extension by default, can be configured
                    is_internal = True
                    extension = config.OPERATOR_EXTENSION_1  # Default to **611
                    transfer_to = None
                    transfer_number = None
                    transfer_text = "Certo, la metto subito in contatto con la segreteria."
                    logger.info(f"Business hours transfer: Using internal extension {extension}")
                
                return {
                    "action": "transfer",
                    "text": transfer_text,
                    "transfer": True,
                    "transfer_to": transfer_to,
                    "is_internal_extension": is_internal,
                    "extension": extension,
                    "transfer_via_number": transfer_number,  # FRITZ!Box number to use for transfer
                    "end_call": False
                }
            
            # Check if appointment booking
            if response.get("book_appointment", False):
                appointment_result = self.appointment_manager.create_appointment(
                    patient_name=response.get("patient_name"),
                    patient_phone=context.get("from_number", ""),
                    visit_type=response.get("visit_type")
                )
                
                if appointment_result["success"]:
                    return {
                        "action": "say",
                        "text": f"Perfetto, ho prenotato l'appuntamento per {appointment_result['date']} alle {appointment_result['time']}. Posso aiutarla in altro?",
                        "transfer": False,
                        "end_call": False
                    }
                else:
                    # Appointment booking failed - transfer to operator
                    office_result = BusinessRules.is_office_hours()
                    is_open = office_result[0]
                    
                    if not is_open:
                        # Out of hours transfer
                        return {
                            "action": "transfer",
                            "text": "Mi dispiace, non sono riuscita a prenotare l'appuntamento. "
                                    "La metto in contatto con l’operatore reperibile.",
                            "transfer": True,
                            "transfer_to": config.OUT_OF_HOURS_MOBILE,
                            "is_internal_extension": False,
                            "extension": None,
                            "transfer_via_number": config.OUT_OF_HOURS_TRANSFER_NUMBER,
                            "end_call": False
                        }
                    else:
                        # Business hours - internal extension
                        return {
                            "action": "transfer",
                            "text": "Mi dispiace, non sono riuscita a prenotare l'appuntamento. "
                                    "La metto in contatto con la segreteria.",
                            "transfer": True,
                            "transfer_to": None,
                            "is_internal_extension": True,
                            "extension": config.OPERATOR_EXTENSION_1,
                            "transfer_via_number": None,
                            "end_call": False
                        }
            
            # Check for goodbye/end call
            goodbye_keywords = ["arrivederci", "grazie", "basta", "fine", "niente altro"]
            if any(keyword in transcript.lower() for keyword in goodbye_keywords) and "altro" not in response["text"].lower():
                return {
                    "action": "say",
                    "text": response["text"],
                    "transfer": False,
                    "end_call": True
                }
            
            # Normal response
            return {
                "action": "say",
                "text": response["text"],
                "transfer": False,
                "end_call": False
            }
            
        except Exception as e:
            logger.error(f"Error processing speech text: {e}", exc_info=True)
            return {
                "action": "say",
                "text": "Mi dispiace, non ho capito. Può ripetere?",
                "transfer": False,
                "end_call": False
            }
    
    def end_call(self, call_sid: str):
        """Clean up when call ends."""
        if call_sid in self.conversation_context:
            del self.conversation_context[call_sid]

