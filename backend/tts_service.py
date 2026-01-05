"""Text-to-Speech service using OpenAI TTS API."""
import logging
import sys
import os
import io
from openai import OpenAI

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.config import config

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        # Use "nova" voice for natural, warm Italian female voice
        # "alloy", "echo", "fable", "onyx", "nova", "shimmer" - nova is best for Italian
        self.voice = "nova"  # Natural Italian female voice
        self.model = "tts-1"  # Fast model (tts-1-hd for higher quality but slower)
    
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

