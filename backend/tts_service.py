"""Text-to-Speech service using OpenAI TTS API."""
import logging
from openai import OpenAI
from backend.config import config
import io

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.voice = "nova"  # Good Italian voice
        self.model = "tts-1"  # Fast model
    
    def synthesize(self, text: str, language: str = "it") -> bytes:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert
            language: Language code (default: "it" for Italian)
        
        Returns:
            Audio bytes
        """
        try:
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                language=language if language != "it" else None  # OpenAI TTS auto-detects Italian
            )
            
            # Return audio bytes
            audio_bytes = b""
            for chunk in response.iter_bytes():
                audio_bytes += chunk
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Error in TTS synthesis: {e}")
            return b""

