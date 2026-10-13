import 'dotenv/config';

const EXACT_GREETING = "Hey, it's Remo, representing Score Labs.";

const FALLBACK_TEXT = {
    'en': "I'm sorry, I don't have that information right now, but I'll make sure our team follows up with you directly.",
    'hi': "माफ़ कीजिए, मेरे पास अभी यह जानकारी उपलब्ध नहीं है, लेकिन हमारी टीम आपसे जल्द संपर्क करेगी।",
    'te': "నన్ను క్షమించండి, ప్రస్తుతం నా వద్ద ఆ సమాచారం లేదు, కానీ మా బృందం నేరుగా మిమ్మల్ని సంప్రదిస్తుంది."
};

export default class GeminiService {
    static getOpeningGreeting(service = 'recruitment', contactInfo = {}) {
        const s = String(service || 'recruitment').toLowerCase();
        let intro = EXACT_GREETING;

        if (s === 'recruitment') {
            const role = contactInfo.job_role || contactInfo.role || 'the open position';
            intro += ` I'm calling regarding your application for ${role}. Do you have a couple of minutes to talk?`;
        } else if (s === 'sales') {
            const company = contactInfo.company || 'your team';
            intro += ` I'm reaching out to see if we can help automate voice communications for ${company}. Are you available for a brief chat?`;
        } else {
            intro += ` I'm following up regarding your recent query with customer support. Is now a good time to speak?`;
        }

        return intro;
    }

    static getUniversalFallback(lang = 'en') {
        return FALLBACK_TEXT[lang?.toLowerCase()] || FALLBACK_TEXT['en'];
    }

    static async generateReply(service, contactInfo = {}, conversationHistory = [], callerMessage = null) {
        const apiKey = (process.env.GEMINI_API_KEY || '').trim();
        const model = process.env.GEMINI_MODEL || 'models/gemini-3.8-flash';
        const cleanModel = model.replace('models/', '');
        const lang = contactInfo.preferred_language || 'en';

        // First turn check
        if ((!conversationHistory || conversationHistory.length === 0) && !callerMessage) {
            return {
                spoken_response: this.getOpeningGreeting(service, contactInfo),
                detected_language: lang,
                should_end_call: false,
                extracted_fields: {},
                classification: 'IN_PROGRESS',
                call_summary: 'Call initiated. Opening identity greeting delivered.'
            };
        }

        if (!apiKey) {
            console.warn('[GeminiService] GEMINI_API_KEY not configured. Using fallback dialogue.');
            return {
                spoken_response: "Thank you for sharing that. Could you tell me a little more about your background?",
                detected_language: lang,
                should_end_call: false,
                extracted_fields: {},
                classification: 'IN_PROGRESS',
                call_summary: 'Dialogue progression via fallback.'
            };
        }

        const systemPrompt = `
You are Remo, an articulate, empathetic, and professional AI Voice Agent representing Score Labs.
You are on a LIVE telephony call in ${service.toUpperCase()} mode.

### CORE VOICE CONSTRAINTS:
1. Speak in concise, natural telephone dialogue (1-2 sentences, strictly under 30 words per turn).
2. Ask ONE question at a time. Never ask compound or multi-part questions.
3. Active listening: acknowledge what the caller said before transitioning ("Got it, 3 years in React...").
4. If caller speaks Hindi, seamlessly reply in natural Hindi. If caller speaks Telugu, reply in natural Telugu. Default to English.
5. If caller asks something you don't know, use exact fallback:
   - English: "${FALLBACK_TEXT['en']}"
   - Hindi: "${FALLBACK_TEXT['hi']}"
   - Telugu: "${FALLBACK_TEXT['te']}"
6. Never invent salaries, promises, dates, or product capabilities.
7. If caller wants to end the call or is not interested, be polite and set "should_end_call": true.
8. Once core information has been collected and confirmed by caller, thank them and set "should_end_call": true.

### CONTACT CONTEXT:
Name: ${contactInfo.name || 'Caller'}
Phone: ${contactInfo.phone || ''}
Service: ${service}

### JSON OUTPUT SCHEMA ONLY:
You MUST respond with a valid JSON object only (no markdown, no backticks):
{
  "spoken_response": "The exact words Remo will speak out loud",
  "detected_language": "en" | "hi" | "te",
  "should_end_call": false | true,
  "extracted_fields": {},
  "classification": "Accepted / Shortlisted" | "Rejected" | "On Hold" | "INTERESTED" | "NOT_INTERESTED",
  "call_summary": "1-2 sentence factual summary"
}
`;

        const historyLines = [];
        for (const msg of conversationHistory) {
            historyLines.push(`${msg.speaker || 'Unknown'}: ${msg.text || ''}`);
        }
        if (callerMessage) {
            historyLines.push(`Caller: ${callerMessage}`);
        }

        const userPrompt = `Conversation History:\n${historyLines.join('\n')}\n\nGenerate Remo's next spoken response as pure JSON.`;

        const url = `https://generativelanguage.googleapis.com/v1beta/models/${cleanModel}:generateContent?key=${apiKey}`;

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [
                        { role: 'user', parts: [{ text: `${systemPrompt}\n\n${userPrompt}` }] }
                    ],
                    generationConfig: {
                        temperature: 0.1,
                        responseMimeType: 'application/json'
                    }
                })
            });

            if (res.ok) {
                const data = await res.json();
                const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
                const cleanJson = rawText.replace(/```json/g, '').replace(/```/g, '').trim();
                const parsed = JSON.parse(cleanJson);

                return {
                    spoken_response: parsed.spoken_response || this.getUniversalFallback(lang),
                    detected_language: parsed.detected_language || 'en',
                    should_end_call: Boolean(parsed.should_end_call),
                    extracted_fields: parsed.extracted_fields || {},
                    classification: parsed.classification || 'On Hold',
                    call_summary: parsed.call_summary || 'Dialogue completed.'
                };
            } else {
                const errText = await res.text();
                console.error(`[GeminiService] HTTP ${res.status} error:`, errText.slice(0, 150));
            }
        } catch (e) {
            console.error(`[GeminiService] Error calling Gemini:`, e.message);
        }

        // Safe graceful fallback
        return {
            spoken_response: this.getUniversalFallback(lang),
            detected_language: lang,
            should_end_call: true,
            extracted_fields: {},
            classification: 'On Hold',
            call_summary: 'Call handled via universal fallback.'
        };
    }
}
