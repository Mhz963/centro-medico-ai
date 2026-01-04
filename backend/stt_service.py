"""Speech-to-Text service using OpenAI Whisper API."""
import logging
from openai import OpenAI
from backend.config import config

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def transcribe(self, audio_data: bytes, language: str = "it") -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio bytes
            language: Language code (default: "it" for Italian)
        
        Returns:
            Transcribed text
        """
        try:
            # Save audio to temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            try:
                # Transcribe using Whisper API
                with open(tmp_file_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language
                    )
                
                return transcript.text
            finally:
                # Clean up temp file
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            return ""

