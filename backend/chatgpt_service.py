"""ChatGPT service for conversation handling."""
import logging
import sys
import os
from openai import OpenAI
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.config import config

logger = logging.getLogger(__name__)

class ChatGPTService:
    """ChatGPT API service."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "prompts",
                "system_prompt.txt"
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            return "Sei una segretaria telefonica professionale per Centro Medico Gargano."
    
    def get_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get response from ChatGPT.
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation messages
        
        Returns:
            Response dictionary with text and metadata
        """
        try:
            # Build messages
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages for context
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get model from config
            try:
                from backend.config import config
                model = config.OPENAI_MODEL
            except (ImportError, AttributeError):
                model = "gpt-4o-mini"  # Fallback
            
            # Call ChatGPT API
            response = self.client.chat.completions.create(
                model=model,  # Use configured model (gpt-4o-mini or gpt-4.1-mini)
                messages=messages,
                temperature=0.7,
                max_tokens=300,  # Shorter responses for phone calls
                presence_penalty=0.6  # Encourage variety
            )
            
            response_text = response.choices[0].message.content
            
            # Parse response for special actions
            result = {
                "text": response_text,
                "transfer_to_operator": self._should_transfer(response_text, user_message),
                "book_appointment": self._should_book_appointment(response_text, user_message),
                "patient_name": None,
                "visit_type": None
            }
            
            # Extract appointment details if booking
            if result["book_appointment"]:
                result["patient_name"] = self._extract_patient_name(user_message, response_text)
                result["visit_type"] = self._extract_visit_type(user_message)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in ChatGPT API call: {e}")
            return {
                "text": "Mi dispiace, non sono riuscita a processare la richiesta. La metto in contatto con un operatore.",
                "transfer_to_operator": True,
                "book_appointment": False
            }
    
    def _should_transfer(self, response_text: str, user_message: str) -> bool:
        """Check if call should be transferred to operator."""
        # Check user message for explicit operator requests (HIGH PRIORITY)
        user_lower = user_message.lower()
        user_transfer_keywords = [
            "operatore", "segretaria", "una persona", "parlare con qualcuno",
            "parlare con la segretaria", "voglio parlare con", "metto in contatto",
            "trasferisci", "trasferire", "voglio un operatore", "voglio la segretaria",
            "posso parlare con", "devo parlare con", "parlare con operatore"
        ]
        if any(keyword in user_lower for keyword in user_transfer_keywords):
            logger.info(f"Transfer detected from user message: {user_message}")
            return True
        
        # Check response text for transfer indicators
        response_lower = response_text.lower()
        transfer_keywords = [
            "metto in contatto",
            "metto subito in contatto",
            "trasferisco",
            "operatore",
            "segretaria"
        ]
        if any(keyword in response_lower for keyword in transfer_keywords):
            logger.info(f"Transfer detected from response: {response_text}")
            return True
        
        return False
    
    def _should_book_appointment(self, response_text: str, user_message: str) -> bool:
        """Check if appointment should be booked."""
        booking_keywords = [
            "prenotare", "prenotazione", "prenotato", "prenotiamo",
            "appuntamento", "appuntamenti",
            "visita", "visite",
            "disponibilità", "disponibile",
            "fissare", "fissiamo", "fisso",
            "prenota", "prenotiamo", "vorrei prenotare", "voglio prenotare",
            "fissare un appuntamento", "fissare appuntamento"
        ]
        user_lower = user_message.lower()
        response_lower = response_text.lower()
        
        # Check if user explicitly wants to book
        user_wants_booking = any(keyword in user_lower for keyword in booking_keywords)
        
        # Check if response confirms booking or asks for details
        response_confirms = any([
            "prenot" in response_lower,
            "appuntamento" in response_lower and ("prenot" in response_lower or "fiss" in response_lower),
            "fissiamo" in response_lower,
            "disponibile" in response_lower and ("quando" in response_lower or "orario" in response_lower),
            "quando" in response_lower and ("visita" in response_lower or "appuntamento" in response_lower),
            "nome" in response_lower and ("appuntamento" in response_lower or "prenot" in response_lower)
        ])
        
        # If user wants to book and AI is confirming/asking details, proceed
        should_book = user_wants_booking and response_confirms
        if should_book:
            logger.info(f"Appointment booking detected - user: {user_message}, response: {response_text}")
        return should_book
    
    def _extract_patient_name(self, user_message: str, response_text: str) -> Optional[str]:
        """Extract patient name from conversation."""
        try:
            from backend.utils import extract_name
        except ImportError:
            try:
                from utils import extract_name
            except ImportError:
                # Fallback: simple extraction
                import re
                patterns = [
                    r'mi chiamo\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                    r'sono\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, user_message, re.IGNORECASE)
                    if match:
                        return match.group(1).title()
                return None
        
        # Try to extract from user message
        name = extract_name(user_message)
        if name:
            return name
        
        # Try to extract from response (if AI repeated it)
        name = extract_name(response_text)
        if name:
            return name
        
        return None
    
    def _extract_visit_type(self, user_message: str) -> str:
        """Extract visit type from conversation."""
        # Simple extraction - can be improved
        visit_types = {
            "eco-color-doppler": ["doppler", "ecodoppler", "circolazione", "gambe"],
            "emorroidi": ["emorroidi", "emorroide"],
            "medicina estetica": ["estetica", "botox", "filler"]
        }
        
        user_lower = user_message.lower()
        for visit_type, keywords in visit_types.items():
            if any(keyword in user_lower for keyword in keywords):
                return visit_type
        
        return "visita generica"

