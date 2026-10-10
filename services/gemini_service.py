"""
TakeRemo — Gemini LLM Service Layer
Configures Gemini 3.8 Flash (temperature=0.1) with domain Markdown instructions,
multilingual detection (English, Hindi, Telugu), strict opening identity,
and structured JSON extraction.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
import google.generativeai as genai

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS_DIR = os.path.join(BASE_DIR, 'docs', 'agent-hari')

# Universal fallbacks required by specification
FALLBACK_TEXT = {
    'en': "Our team will contact you regarding this. Thank you for your time.",
    'hi': "हमारी टीम इस बारे में आपसे संपर्क करेगी। अपना समय देने के लिए धन्यवाद।",
    'te': "మా టీమ్ ఈ విషయం గురించి మిమ్మల్ని సంప్రదిస్తుంది. మీ సమయానికి ధన్యవాదాలు。"
}

EXACT_GREETING = "Hey, it's Remo, representing Score Labs."


def load_domain_instruction(service: str) -> str:
    """Loads markdown file for the specific service from docs/agent-hari/ or repo root."""
    mapping = {
        'recruitment': ['05-recruitment-agent.md', 'recruitment.md'],
        'sales': ['06-sales-agent.md', 'sales.md'],
        'support': ['07-customer-support-agent.md', 'customer-support.md', 'customer_support.md']
    }
    filenames = mapping.get(service.lower(), ['05-recruitment-agent.md'])
    for fn in filenames:
        path = os.path.join(DOCS_DIR, fn)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        path_root = os.path.join(BASE_DIR, fn)
        if os.path.exists(path_root):
            with open(path_root, 'r', encoding='utf-8') as f:
                return f.read()
    return f"Domain instructions for {service} mode."


class GeminiService:
    _configured = False

    @classmethod
    def get_opening_greeting(cls) -> str:
        return EXACT_GREETING

    @classmethod
    def get_universal_fallback(cls, lang: str = 'en') -> str:
        return FALLBACK_TEXT.get(lang.lower(), FALLBACK_TEXT['en'])

    @classmethod
    def get_system_prompt(cls, service: str) -> str:
        return load_domain_instruction(service)

    @classmethod
    def _init_gemini(cls):
        if not cls._configured:
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is missing.")
            genai.configure(api_key=api_key)
            cls._configured = True

    @classmethod
    def generate_reply(
        cls,
        service: str,
        contact_info: Dict[str, Any],
        transcript_history: List[Dict[str, str]],
        caller_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes conversation turn using Gemini.
        Returns structured JSON with:
        - spoken_response: string to be voiced by Remo
        - detected_language: 'en', 'hi', or 'te'
        - should_end_call: bool
        - extracted_fields: dict
        - classification: str
        - call_summary: str
        """
        cls._init_gemini()
        model_name = os.environ.get('GEMINI_MODEL', 'models/gemini-3.8-flash')
        temp_str = os.environ.get('GEMINI_TEMPERATURE', '0.1')
        try:
            temperature = float(temp_str)
        except Exception:
            temperature = 0.1

        domain_instructions = load_domain_instruction(service)

        # First turn check: if transcript_history is empty, return exact greeting
        if not transcript_history and not caller_message:
            greeting_lang = contact_info.get('preferred_language', 'en') or 'en'
            intro = f"{EXACT_GREETING}"
            # Add polite contextual opener depending on service
            if service == 'recruitment':
                role = contact_info.get('job_role') or contact_info.get('extra', {}).get('job_role', 'the open position')
                intro += f" I'm calling regarding your application for {role}. Do you have a couple of minutes to talk?"
            elif service == 'sales':
                company = contact_info.get('company') or contact_info.get('extra', {}).get('company', '')
                intro += f" I'm reaching out to see if we can help automate voice communications for {company or 'your team'}. Are you available for a brief chat?"
            else:
                intro += " I'm following up regarding your recent query with customer support. Is now a good time to speak?"

            return {
                "spoken_response": intro,
                "detected_language": greeting_lang if greeting_lang in ('en', 'hi', 'te') else 'en',
                "should_end_call": False,
                "extracted_fields": {},
                "classification": "IN_PROGRESS",
                "call_summary": "Call initiated. Opening identity greeting delivered."
            }

        # Build full conversation prompt
        system_prompt = f"""
You are Remo, an articulate and empathetic AI Voice Agent representing Score Labs.
You are currently on a live telephone call in {service.upper()} mode.

### IDENTITY & FIRST SPOKEN SENTENCE:
Your greeting identity is always: "{EXACT_GREETING}"

### LANGUAGE GUIDELINES:
- Default to English.
- If caller responds in Hindi, seamlessly switch and continue in natural conversational Hindi.
- If caller responds in Telugu, seamlessly switch and continue in natural conversational Telugu.
- Never use robotic machine translations. Preserve names, numbers, technical terms, and Score Labs branding.

### UNIVERSAL FALLBACK:
If you do not know the answer, lack verified data, cannot understand the query, or the caller asks for information outside authorized scope, DO NOT GUESS.
Use this exact fallback in the caller's language:
- English: "{FALLBACK_TEXT['en']}"
- Hindi: "{FALLBACK_TEXT['hi']}"
- Telugu: "{FALLBACK_TEXT['te']}"

### CONVERSATION PRINCIPLES:
1. Speak concisely: 1 to 2 short sentences per turn (under 30 words).
2. Ask ONE question at a time.
3. Active listening: acknowledge the caller's answer before pivoting.
4. Do not invent details, salaries, pricing, features, or promises.
5. If the caller declines to talk, requests human transfer, or asks to stop receiving calls, respect it immediately, close politely, and set should_end_call to true.
6. Once you have collected the core information, summarize it and ask the caller to confirm if it is correct.
7. Once the caller confirms the information is correct, say thank you and end the call by setting should_end_call to true.

### DOMAIN INSTRUCTIONS:
{domain_instructions}

### CONTACT CONTEXT:
Name: {contact_info.get('name', 'Caller')}
Phone: {contact_info.get('phone', '')}
Notes / Staged Data: {json.dumps(contact_info.get('extra', {}))}

### OUTPUT FORMAT:
You MUST output ONLY a valid JSON object with the following schema:
{{
  "spoken_response": "Exact words Remo will speak out loud to the caller",
  "detected_language": "en" | "hi" | "te",
  "should_end_call": true | false,
  "extracted_fields": {{
     // Extracted facts (education, skills, experience, interest, category, etc.)
  }},
  "classification": "{'Accepted / Shortlisted' if service=='recruitment' else 'INTERESTED'} | {'Rejected' if service=='recruitment' else 'NOT_INTERESTED'} | {'On Hold' if service=='recruitment' else 'FOLLOW_UP'} | ...",
  "call_summary": "Concise 1-2 sentence factual summary of the discussion"
}}
"""

        # Format conversation messages
        history_formatted = []
        for turn in transcript_history:
            history_formatted.append(f"{turn.get('speaker', 'Unknown')}: {turn.get('text', '')}")
        if caller_message:
            history_formatted.append(f"Caller: {caller_message}")

        user_content = f"Conversation History:\n" + "\n".join(history_formatted) + "\n\nGenerate the next response as valid JSON."

        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json"
                )
            )
            response = model.generate_content([system_prompt, user_content])
            raw_text = response.text.strip()

            # Clean json fences if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            parsed = json.loads(raw_text.strip())
            return {
                "spoken_response": parsed.get("spoken_response", FALLBACK_TEXT['en']),
                "detected_language": parsed.get("detected_language", "en"),
                "should_end_call": bool(parsed.get("should_end_call", False)),
                "extracted_fields": parsed.get("extracted_fields", {}),
                "classification": parsed.get("classification", "On Hold" if service == 'recruitment' else "PENDING"),
                "call_summary": parsed.get("call_summary", "Conversation ongoing.")
            }
        except Exception as e:
            # Fallback on LLM failure
            lang = contact_info.get('preferred_language', 'en')
            fallback_msg = FALLBACK_TEXT.get(lang, FALLBACK_TEXT['en'])
            return {
                "spoken_response": fallback_msg,
                "detected_language": lang,
                "should_end_call": True,
                "extracted_fields": {},
                "classification": "On Hold" if service == 'recruitment' else "REVIEW_REQUIRED",
                "call_summary": f"Fallback triggered due to service interruption: {str(e)}"
            }
