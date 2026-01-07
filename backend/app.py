"""Main FastAPI application for Centro Medico Gargano AI Voice Assistant."""
import sys
import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.config import config
from backend.call_handler import CallHandler

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

@app.get("/webhook/voice")
async def voice_webhook_get():
    """GET handler for webhook endpoint (for testing)."""
    return JSONResponse({
        "message": "This endpoint is for POST requests from Twilio",
        "endpoint": "/webhook/voice",
        "method": "POST",
        "description": "Twilio webhook for incoming voice calls"
    })

# Compatibility routes:
# Some Twilio console setups accidentally point to `/webhook` or add a trailing slash.
# We accept those and route to the same handlers so Twilio always receives valid TwiML.
@app.get("/webhook")
@app.get("/webhook/")
async def webhook_root_get():
    """GET handler for legacy/short webhook endpoint (for testing)."""
    return JSONResponse({
        "message": "This endpoint is for POST requests from Twilio",
        "endpoint": "/webhook",
        "recommended_endpoint": "/webhook/voice",
        "method": "POST"
    })

@app.post("/webhook/voice")
@app.post("/webhook/voice/")
@app.post("/webhook")
@app.post("/webhook/")
async def voice_webhook(request: Request):
    """
    Twilio webhook endpoint for incoming voice calls.
    This is where calls from FRITZ!Box will arrive.
    ALWAYS returns TwiML - never JSON.
    """
    # Always return TwiML, never JSON - wrap entire function
    try:
        # Check if call handler is available
        if call_handler is None:
            logger.error("Call handler not initialized - cannot process call")
            response = VoiceResponse()
            response.say("Scusi, il servizio non è temporaneamente disponibile. Riprovi più tardi.", language="it-IT", voice="alice")
            return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        # Get form data from Twilio - handle errors gracefully
        try:
            form_data = await request.form()
            call_sid = form_data.get("CallSid", "unknown")
            from_number = form_data.get("From", "")
            to_number = form_data.get("To", "")
        except Exception as form_error:
            logger.error(f"Error parsing form data: {form_error}")
            # Return valid TwiML even if form data is missing
            call_sid = "unknown"
            from_number = ""
            to_number = ""
            form_data = {}
        
        logger.info(f"Incoming call - SID: {call_sid}, From: {from_number}, To: {to_number}")
        
        # Handle the call using call handler
        try:
            call_result = call_handler.handle_call(call_sid, from_number)
        except Exception as handler_error:
            logger.error(f"Error in call handler: {handler_error}", exc_info=True)
            # Return valid TwiML with error message
            response = VoiceResponse()
            response.say("Buongiorno, Centro Medico Gargano. Come posso aiutarla?", language="it-IT", voice="alice")
            gather = Gather(
                input="speech",
                language="it-IT",
                speech_timeout="auto",
                action="/webhook/voice/process",
                method="POST",
                timeout=10,
                bargeIn="true"
            )
            gather.say("Non ho capito, può ripetere?", language="it-IT", voice="alice")
            response.append(gather)
            return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        # Create TwiML response
        response = VoiceResponse()
        
        # If transfer needed (operator request) - handle before Gather
        if call_result.get("transfer"):
            try:
                from backend.operator_transfer import OperatorTransfer
            except ImportError:
                try:
                    from operator_transfer import OperatorTransfer
                except ImportError:
                    logger.error("OperatorTransfer module not found")
                    # Fallback to simple TwiML
                    response.say("Un attimo, la metto in contatto con un operatore.", language="it-IT", voice="alice")
                    return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
            
            try:
                transfer_response = OperatorTransfer.create_transfer_response(
                    operator_number=call_result.get("transfer_to"),
                    is_internal_extension=call_result.get("is_internal_extension", False),
                    extension=call_result.get("extension"),
                    message=call_result.get("text", "Un attimo, la metto in contatto con un operatore."),
                    via_number=call_result.get("transfer_via_number")
                )
                return Response(content=transfer_response, media_type="application/xml", headers={"Content-Type": "text/xml"})
            except Exception as transfer_error:
                logger.error(f"Error creating transfer response: {transfer_error}", exc_info=True)
                # Fallback to simple TwiML
                response.say("Un attimo, la metto in contatto con un operatore.", language="it-IT", voice="alice")
                return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        # Say greeting or message using Twilio's built-in TTS (reliable, no external dependencies)
        text_to_speak = call_result.get("text", "Buongiorno, Centro Medico Gargano, come posso aiutarla?")
        
        # Gather user input (speech) with barge-in enabled
        gather = Gather(
            input="speech",
            language="it-IT",
            speech_timeout="auto",
            action="/webhook/voice/process",
            method="POST",
            timeout=10,
            bargeIn="true"
        )
        
        # Use Twilio's built-in Say - reliable and works immediately
        gather.say(text_to_speak, language="it-IT", voice="alice")
        response.append(gather)
        
        # If no input, repeat
        response.say("Non ho capito, può ripetere?", language="it-IT", voice="alice")
        
        response.redirect("/webhook/voice")
        
        return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
    except Exception as e:
        # Catch-all exception handler - ALWAYS return TwiML
        logger.error(f"Unexpected error in voice webhook: {e}", exc_info=True)
        response = VoiceResponse()
        error_text = "Buongiorno, Centro Medico Gargano. Come posso aiutarla?"
        response.say(error_text, language="it-IT", voice="alice")
        gather = Gather(
            input="speech",
            language="it-IT",
            speech_timeout="auto",
            action="/webhook/voice/process",
            method="POST",
            timeout=10,
            bargeIn="true"
        )
        gather.say("Non ho capito, può ripetere?", language="it-IT", voice="alice")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})


@app.get("/webhook/voice/transfer-status")
@app.get("/webhook/voice/transfer-status/")
async def transfer_status_get():
    """GET handler for transfer status endpoint (for testing)."""
    return JSONResponse({
        "message": "This endpoint is for POST requests from Twilio Dial action callback",
        "endpoint": "/webhook/voice/transfer-status",
        "method": "POST"
    })


@app.post("/webhook/voice/transfer-status")
@app.post("/webhook/voice/transfer-status/")
async def transfer_status(request: Request):
    """
    Twilio Dial action callback endpoint.
    MUST return valid TwiML to avoid Twilio 'application error' after transfer attempts.
    """
    try:
        form_data = await request.form()
    except Exception:
        form_data = {}

    dial_call_status = form_data.get("DialCallStatus", "")
    call_sid = form_data.get("CallSid", "")
    logger.info(f"Transfer status callback - CallSID: {call_sid}, DialCallStatus: {dial_call_status}")

    response = VoiceResponse()

    # If transfer failed or no-answer, fall back to the assistant flow
    if dial_call_status and dial_call_status.lower() not in ("completed", "answered"):
        response.say(
            "Mi dispiace, non riesco a metterla in contatto in questo momento. Posso aiutarla io?",
            language="it-IT",
            voice="alice",
        )
        response.redirect("/webhook/voice")
        return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})

    # If transfer completed, end gracefully
    response.hangup()
    return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})

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
    """Process speech input from caller. ALWAYS returns TwiML - never JSON."""
    # Always return TwiML, never JSON - wrap entire function
    try:
        # Check if call handler is available
        if call_handler is None:
            logger.error("Call handler not initialized - cannot process voice")
            response = VoiceResponse()
            response.say("Scusi, il servizio non è temporaneamente disponibile. Riprovi più tardi.", language="it-IT", voice="alice")
            return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        # Get form data from Twilio - handle errors gracefully
        try:
            form_data = await request.form()
            speech_result = form_data.get("SpeechResult", "")
            call_sid = form_data.get("CallSid", "")
        except Exception as form_error:
            logger.error(f"Error parsing form data: {form_error}")
            speech_result = ""
            call_sid = "unknown"
            form_data = {}
        
        logger.info(f"Processing speech - CallSID: {call_sid}, Speech: {speech_result}")
        
        if not speech_result:
            # No speech detected, ask to repeat
            response = VoiceResponse()
            gather = Gather(
                input="speech",
                language="it-IT",
                speech_timeout="auto",
                action="/webhook/voice/process",
                method="POST",
                timeout=10,
                bargeIn="true"
            )
            gather.say("Non ho capito, può ripetere?", language="it-IT", voice="alice")
            response.append(gather)
            response.redirect("/webhook/voice/process")
            return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        # Process speech with ChatGPT (Twilio already did STT, so we use the text directly)
        try:
            call_result = call_handler.process_speech_text(call_sid, speech_result)
        except Exception as process_error:
            logger.error(f"Error processing speech text: {process_error}", exc_info=True)
            # Return valid TwiML with error message
            response = VoiceResponse()
            error_text = "Mi dispiace, non ho capito. Può ripetere?"
            gather = Gather(
                input="speech",
                language="it-IT",
                speech_timeout="auto",
                action="/webhook/voice/process",
                method="POST",
                timeout=10,
                bargeIn="true"
            )
            gather.say(error_text, language="it-IT", voice="alice")
            response.append(gather)
            return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        response = VoiceResponse()
        
        # Handle different actions
        if call_result.get("action") == "transfer":
            # Transfer to operator
            try:
                from backend.operator_transfer import OperatorTransfer
            except ImportError:
                try:
                    from operator_transfer import OperatorTransfer
                except ImportError:
                    logger.error("OperatorTransfer module not found")
                    # Fallback to simple TwiML
                    response.say("Un attimo, la metto in contatto con un operatore.", language="it-IT", voice="alice")
                    return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
            
            try:
                transfer_response = OperatorTransfer.create_transfer_response(
                    operator_number=call_result.get("transfer_to"),
                    is_internal_extension=call_result.get("is_internal_extension", False),
                    extension=call_result.get("extension"),
                    message=call_result.get("text", "Un attimo, la metto in contatto con un operatore."),
                    via_number=call_result.get("transfer_via_number")
                )
                return Response(content=transfer_response, media_type="application/xml", headers={"Content-Type": "text/xml"})
            except Exception as transfer_error:
                logger.error(f"Error creating transfer response: {transfer_error}", exc_info=True)
                # Fallback to simple TwiML
                response.say("Un attimo, la metto in contatto con un operatore.", language="it-IT", voice="alice")
                return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        elif call_result.get("action") == "say":
            # Say response - use Gather with barge-in for proper interruption
            text_to_speak = call_result.get("text", "Mi dispiace, non ho capito.")
            
            gather = Gather(
                input="speech",
                language="it-IT",
                speech_timeout="auto",
                action="/webhook/voice/process",
                method="POST",
                timeout=10,
                bargeIn="true"
            )
            
            # Use Twilio's built-in Say - reliable
            gather.say(text_to_speak, language="it-IT", voice="alice")
            response.append(gather)
        
        # Check if call should end (e.g., appointment booked, goodbye)
        if call_result.get("end_call", False):
            response.say("Le auguro una buona giornata. Arrivederci.", language="it-IT", voice="alice")
            response.hangup()
            return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
        # Timeout fallback
        response.say("Non ho capito, può ripetere?", language="it-IT", voice="alice")
        response.redirect("/webhook/voice/process")
        
        return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})
        
    except Exception as e:
        # Catch-all exception handler - ALWAYS return TwiML
        logger.error(f"Unexpected error processing voice: {e}", exc_info=True)
        response = VoiceResponse()
        error_text = "Mi dispiace, non ho capito. Può ripetere?"
        gather = Gather(
            input="speech",
            language="it-IT",
            speech_timeout="auto",
            action="/webhook/voice/process",
            method="POST",
            timeout=10,
            bargeIn="true"
        )
        gather.say(error_text, language="it-IT", voice="alice")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml", headers={"Content-Type": "text/xml"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)

