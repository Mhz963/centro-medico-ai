/**
 * Twilio Function: Handle Call Transfers
 * 
 * This function handles transfers based on office hours:
 * - Office hours (Mon-Fri, 9:00-19:00 Europe/Rome): Transfer to **611 or **612
 * - Outside hours: Transfer to +39 348 703 5744
 * 
 * To use this:
 * 1. Create a new Twilio Function in Twilio Console
 * 2. Paste this code
 * 3. Configure ElevenLabs Agent to call this function when transfer is needed
 * 4. Set environment variables if needed
 */

exports.handler = function(context, event, callback) {
    const twiml = new Twilio.twiml.VoiceResponse();
    
    // Get current time in Europe/Rome timezone
    const now = new Date();
    const romeTime = new Date(now.toLocaleString("en-US", {timeZone: "Europe/Rome"}));
    
    const hour = romeTime.getHours();
    const day = romeTime.getDay(); // 0=Sunday, 1=Monday, etc.
    
    // Office hours: Monday-Friday (1-5), 9:00-19:00
    const isOfficeHours = (day >= 1 && day <= 5) && (hour >= 9 && hour < 19);
    
    // Get transfer preference from event (if provided by ElevenLabs Agent)
    const extensionPreference = event.extension || '**611'; // Default to **611
    
    if (isOfficeHours) {
        // Office hours: Transfer to internal extension
        const extension = extensionPreference.startsWith('**') 
            ? extensionPreference 
            : '**' + extensionPreference;
        
        twiml.say('Un attimo, la metto in contatto con la segreteria.', {
            language: 'it-IT',
            voice: 'alice'
        });
        
        const dial = twiml.dial({
            timeout: 30,
            action: '/webhook/voice/transfer-status',
            method: 'POST'
        });
        
        // Transfer to FRITZ!Box extension (format: **611 or **612)
        dial.number(extension);
        
        console.log(`Office hours transfer to extension: ${extension}`);
    } else {
        // Outside hours: Transfer to mobile
        const mobileNumber = '+393487035744'; // +39 348 703 5744
        
        twiml.say('Centro Medico Gargano è attualmente chiuso, ma la metto in contatto con l\'operatore reperibile.', {
            language: 'it-IT',
            voice: 'alice'
        });
        
        const dial = twiml.dial({
            timeout: 30,
            action: '/webhook/voice/transfer-status',
            method: 'POST'
        });
        
        dial.number(mobileNumber);
        
        console.log(`Outside hours transfer to mobile: ${mobileNumber}`);
    }
    
    callback(null, twiml);
};

