"""Main FastAPI application for Centro Medico Gargano AI Voice Assistant."""
import sys
import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Gather, Play
from twilio.request_validator import RequestValidator
import logging
from typing import Dict, Any
from urllib.parse import quote

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.config import config
from backend.call_handler import CallHandler
from backend.tts_service import TTSService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Centro Medico Gargano AI Voice Assistant")

# Initialize call handler with error handling
try:
    call_handler = CallHandler()
    logger.info("Call handler initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize call handler: {e}")
    call_handler = None

# Initialize TTS service for natural voice
try:
    tts_service = TTSService()
    logger.info("TTS service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize TTS service: {e}")
    tts_service = None

@app.on_event("startup")
async def startup_event():
    """Check configuration on startup."""
    logger.info("Application starting up...")
    
    # Check critical environment variables
    missing_vars = []
    if not config.OPENAI_API_KEY:
        missing_vars.append("OPENAI_API_KEY")
    if not config.TWILIO_ACCOUNT_SID:
        missing_vars.append("TWILIO_ACCOUNT_SID")
    if not config.TWILIO_API_KEY_SID:
        missing_vars.append("TWILIO_API_KEY_SID")
    if not config.TWILIO_API_KEY_SECRET:
        missing_vars.append("TWILIO_API_KEY_SECRET")
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    else:
        logger.info("All critical environment variables are set")
    
    if call_handler is None:
        logger.error("Call handler failed to initialize - some features may not work")
    else:
        logger.info("Application ready to handle calls")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Centro Medico Gargano AI Voice Assistant"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/audio/tts")
async def get_tts_audio(request: Request):
    """
    Generate and serve OpenAI TTS audio for natural Italian voice.
    Query parameter: text (URL encoded)
    """
    if tts_service is None:
        return Response(content="TTS service not available", status_code=503)
    
    try:
        text = request.query_params.get("text", "")
        if not text:
            return Response(content="Missing text parameter", status_code=400)
        
        # Generate audio using OpenAI TTS
        audio_bytes = tts_service.synthesize(text, language="it")
        
        if not audio_bytes:
            return Response(content="Failed to generate audio", status_code=500)
        
        # Return audio as MP3
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=tts.mp3",
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        logger.error(f"Error generating TTS audio: {e}")
        return Response(content=f"Error: {str(e)}", status_code=500)

@app.get("/webhook/voice")
async def voice_webhook_get():
    """GET handler for webhook endpoint (for testing)."""
    return JSONResponse({
        "message": "This endpoint is for POST requests from Twilio",
        "endpoint": "/webhook/voice",
        "method": "POST",
        "description": "Twilio webhook for incoming voice calls"
    })

@app.post("/webhook/voice")
async def voice_webhook(request: Request):
    """
    Twilio webhook endpoint for incoming voice calls.
    This is where calls from FRITZ!Box will arrive.
    """
    if call_handler is None:
        logger.error("Call handler not initialized - cannot process call")
        response = VoiceResponse()
        response.say("Sorry, the service is temporarily unavailable.", language="it")
        return Response(content=str(response), media_type="application/xml")
    
    try:
        # Get form data from Twilio
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From", "")
        to_number = form_data.get("To", "")
        
        logger.info(f"Incoming call - SID: {call_sid}, From: {from_number}, To: {to_number}")
        
        # Handle the call using call handler
        call_result = call_handler.handle_call(call_sid, from_number)
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Say greeting or message using OpenAI TTS for natural voice
        if call_result.get("action") == "say":
            text_to_speak = call_result.get("text", "Buongiorno, Centro Medico Gargano, come posso aiutarla?")
            # Use OpenAI TTS endpoint for natural Italian voice
            # Get base URL from request
            base_url = str(request.base_url).rstrip('/')
            tts_url = f"{base_url}/audio/tts?text={quote(text_to_speak)}"
            response.play(tts_url)
        
        # If transfer needed (operator request)
        if call_result.get("transfer"):
            try:
                from backend.operator_transfer import OperatorTransfer
            except ImportError:
                from operator_transfer import OperatorTransfer
            transfer_response = OperatorTransfer.create_transfer_response(
                operator_number=call_result.get("transfer_to"),
                is_internal_extension=call_result.get("is_internal_extension", False),
                extension=call_result.get("extension"),
                message=call_result.get("text", "Un attimo, la metto in contatto con un operatore."),
                via_number=call_result.get("transfer_via_number")
            )
            return Response(content=transfer_response, media_type="application/xml")
        
        # Gather user input (speech) - Twilio's built-in speech recognition
        # bargeIn=True allows caller to interrupt TTS immediately
        gather = Gather(
            input="speech",
            language="it-IT",
            speech_timeout="auto",
            action="/webhook/voice/process",
            method="POST",
            timeout=10,
            bargeIn=True,
            partial_result_callback="/webhook/voice/process",
            partial_result_callback_method="POST"
        )
        response.append(gather)
        
        # If no input, repeat using OpenAI TTS
        repeat_text = "Non ho capito, può ripetere?"
        base_url = str(request.base_url).rstrip('/')
        tts_url = f"{base_url}/audio/tts?text={quote(repeat_text)}"
        response.play(tts_url)
        response.redirect("/webhook/voice")
        
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in voice webhook: {e}", exc_info=True)
        response = VoiceResponse()
        error_text = "Mi dispiace, si è verificato un errore. La prego di richiamare."
        base_url = str(request.base_url).rstrip('/')
        tts_url = f"{base_url}/audio/tts?text={quote(error_text)}"
        response.play(tts_url)
        return Response(content=str(response), media_type="application/xml")

@app.get("/webhook/voice/process")
async def process_voice_get():
    """GET handler for voice process endpoint (for testing)."""
    return JSONResponse({
        "message": "This endpoint is for POST requests from Twilio",
        "endpoint": "/webhook/voice/process",
        "method": "POST",
        "description": "Processes speech input from caller"
    })

@app.post("/webhook/voice/process")
async def process_voice(request: Request):
    """Process speech input from caller."""
    if call_handler is None:
        logger.error("Call handler not initialized - cannot process voice")
        response = VoiceResponse()
        response.say("Sorry, the service is temporarily unavailable.", language="it")
        return Response(content=str(response), media_type="application/xml")
    
    try:
        form_data = await request.form()
        speech_result = form_data.get("SpeechResult", "")
        call_sid = form_data.get("CallSid", "")
        
        logger.info(f"Processing speech - CallSID: {call_sid}, Speech: {speech_result}")
        
        if not speech_result:
            # No speech detected, ask to repeat using OpenAI TTS
            response = VoiceResponse()
            repeat_text = "Non ho capito, può ripetere?"
            base_url = str(request.base_url).rstrip('/')
            tts_url = f"{base_url}/audio/tts?text={quote(repeat_text)}"
            gather = Gather(
                input="speech",
                language="it-IT",
                speech_timeout="auto",
                action="/webhook/voice/process",
                method="POST",
                timeout=10,
                bargeIn=True
            )
            gather.play(tts_url)
            response.append(gather)
            # Fallback if no input
            response.play(tts_url)
            response.redirect("/webhook/voice/process")
            return Response(content=str(response), media_type="application/xml")
        
        # Process speech with ChatGPT (Twilio already did STT, so we use the text directly)
        # In a more advanced setup, we could use our own STT, but Twilio's is fine for now
        call_result = call_handler.process_speech_text(call_sid, speech_result)
        
        response = VoiceResponse()
        
        # Handle different actions
        if call_result.get("action") == "transfer":
            # Transfer to operator
            try:
                from backend.operator_transfer import OperatorTransfer
            except ImportError:
                from operator_transfer import OperatorTransfer
            transfer_response = OperatorTransfer.create_transfer_response(
                operator_number=call_result.get("transfer_to"),
                is_internal_extension=call_result.get("is_internal_extension", False),
                extension=call_result.get("extension"),
                message=call_result.get("text", "Un attimo, la metto in contatto con un operatore."),
                via_number=call_result.get("transfer_via_number")
            )
            return Response(content=transfer_response, media_type="application/xml")
        
        elif call_result.get("action") == "say":
            # Say response using OpenAI TTS for natural voice
            text_to_speak = call_result.get("text", "Mi dispiace, non ho capito.")
            base_url = str(request.base_url).rstrip('/')
            tts_url = f"{base_url}/audio/tts?text={quote(text_to_speak)}"
            response.play(tts_url)
        
        # Check if call should end (e.g., appointment booked, goodbye)
        if call_result.get("end_call", False):
            goodbye_text = "Le auguro una buona giornata. Arrivederci."
            base_url = str(request.base_url).rstrip('/')
            tts_url = f"{base_url}/audio/tts?text={quote(goodbye_text)}"
            response.play(tts_url)
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        # Continue gathering for next input with barge-in enabled
        gather = Gather(
            input="speech",
            language="it-IT",
            speech_timeout="auto",
            action="/webhook/voice/process",
            method="POST",
            timeout=10,
            bargeIn=True
        )
        response.append(gather)
        
        # Timeout fallback
        timeout_text = "Non ho capito, può ripetere?"
        base_url = str(request.base_url).rstrip('/')
        tts_url = f"{base_url}/audio/tts?text={quote(timeout_text)}"
        response.play(tts_url)
        response.redirect("/webhook/voice/process")
        
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing voice: {e}", exc_info=True)
        response = VoiceResponse()
        error_text = "Mi dispiace, si è verificato un errore. Può ripetere?"
        base_url = str(request.base_url).rstrip('/')
        tts_url = f"{base_url}/audio/tts?text={quote(error_text)}"
        gather = Gather(
            input="speech",
            language="it-IT",
            speech_timeout="auto",
            action="/webhook/voice/process",
            method="POST",
            timeout=10,
            bargeIn=True
        )
        gather.play(tts_url)
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)

