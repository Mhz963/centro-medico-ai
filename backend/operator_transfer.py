"""Operator transfer handling."""
import logging
from backend.config import config
from twilio.twiml.voice_response import VoiceResponse, Dial

logger = logging.getLogger(__name__)

class OperatorTransfer:
    """Handle call transfer to operator."""
    
    @staticmethod
    def create_transfer_response(
        operator_number: str = None,
        is_internal_extension: bool = False,
        extension: str = None,
        message: str = None,
        via_number: str = None
    ) -> str:
        """
        Create TwiML response for call transfer.
        
        Args:
            operator_number: Phone number to transfer to (for mobile/out-of-hours)
            is_internal_extension: True if transferring to internal FRITZ!Box extension
            extension: Internal extension number (e.g., "**611" or "**612")
            message: Optional message before transfer
            via_number: Optional FRITZ!Box number to use for transfer (out of hours)
        
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        if message:
            response.say(message, language="it-IT", voice="alice")
        
        dial = Dial()
        
        if is_internal_extension and extension:
            # Transfer to internal FRITZ!Box extension (during business hours)
            # Format: **611 or **612
            logger.info(f"Transferring to internal extension: {extension}")
            dial.number(extension)
        elif operator_number:
            # Transfer to external number (out of hours mobile)
            # If via_number is specified, we'll use it for routing
            logger.info(f"Transferring to {operator_number} via {via_number or 'default'}")
        dial.number(operator_number)
        else:
            # Fallback: try to use configured operator extension
            logger.warning("No operator number specified, using default extension")
            dial.number(config.OPERATOR_EXTENSION_1)
        
        response.append(dial)
        
        return str(response)

