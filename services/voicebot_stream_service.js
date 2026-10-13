/**
 * services/voicebot_stream_service.js
 * Stub WebSocket handler for voicebot streaming.
 * The actual implementation will be connected when the telephony pipeline is active.
 */

/**
 * Handle an incoming WebSocket connection for voicebot.
 * @param {import('ws').WebSocket} ws
 * @param {import('http').IncomingMessage} request
 */
export function handleVoicebotWebsocket(ws, request) {
    console.log('[VoicebotStream] New WebSocket connection from', request.socket?.remoteAddress || 'unknown');

    ws.on('message', (data) => {
        // Echo back for now — real pipeline hooks in here
        try {
            const msg = JSON.parse(data);
            console.log('[VoicebotStream] Received:', msg?.event || 'unknown event');
        } catch (e) {
            // Binary audio data — pipeline processes this
        }
    });

    ws.on('error', (err) => {
        console.error('[VoicebotStream] WebSocket error:', err.message);
    });

    ws.on('close', (code, reason) => {
        console.log('[VoicebotStream] Connection closed:', code);
    });

    // Send initial handshake
    ws.send(JSON.stringify({ event: 'connected', service: 'TakeRemo VoiceBot Stream' }));
}
