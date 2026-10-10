"""
TakeRemo — Sarvam AI Speech Service Layer
Provides Text-to-Speech (TTS) using 'bulbul:v3' and Speech-to-Text (STT) using 'saaras:v2'.
Handles multilingual audio generation (English, Hindi, Telugu) with safe fallbacks.
"""

import os
import io
import base64
import requests
from typing import Dict, Any, Optional, Tuple

LANGUAGE_CODE_MAP = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'te': 'te-IN'
}


class SarvamService:
    @classmethod
    def get_api_key(cls) -> str:
        key = os.environ.get('SARVAM_API') or os.environ.get('SARVAM_API_KEY')
        if not key:
            raise ValueError("SARVAM_API key is not configured in backend environment.")
        return key.strip()

    @classmethod
    def text_to_speech(cls, text: str, language: str = 'en') -> Optional[str]:
        """
        Converts text into audio using Sarvam AI TTS (bulbul:v3).
        Returns base64 encoded audio string or None on failure.
        """
        if not text or not text.strip():
            return None

        key = cls.get_api_key()
        lang_code = LANGUAGE_CODE_MAP.get(language.lower(), 'en-IN')

        payload = {
            "inputs": [text.strip()],
            "target_language_code": lang_code,
            "speaker": "aditya",
            "model": "bulbul:v3"
        }

        try:
            res = requests.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={
                    "api-subscription-key": key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            if res.status_code == 200:
                data = res.json()
                audios = data.get("audios")
                if audios and len(audios) > 0:
                    return audios[0]
            print(f"[SarvamService] TTS warning (HTTP {res.status_code}): {res.text[:150]}")
            return None
        except Exception as e:
            print(f"[SarvamService] TTS request error: {e}")
            return None

    @classmethod
    def speech_to_text(cls, audio_bytes: bytes, filename: str = "audio.wav", language: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Transcribes audio bytes using Sarvam AI STT (saaras:v2).
        Returns (transcript_text, detected_language).
        """
        if not audio_bytes:
            return None, None

        key = cls.get_api_key()
        files = {
            'file': (filename, audio_bytes, 'audio/wav')
        }
        data = {
            'model': 'saaras:v3'
        }
        if language and language in LANGUAGE_CODE_MAP:
            data['language_code'] = LANGUAGE_CODE_MAP[language]

        try:
            res = requests.post(
                "https://api.sarvam.ai/speech-to-text",
                headers={
                    "api-subscription-key": key
                },
                files=files,
                data=data,
                timeout=20
            )
            if res.status_code == 200:
                resp_json = res.json()
                transcript = resp_json.get("transcript", "")
                detected = resp_json.get("language_code", "en")
                short_lang = "en"
                if "hi" in str(detected).lower():
                    short_lang = "hi"
                elif "te" in str(detected).lower():
                    short_lang = "te"
                return transcript, short_lang
            print(f"[SarvamService] STT warning (HTTP {res.status_code}): {res.text[:150]}")
            return None, None
        except Exception as e:
            print(f"[SarvamService] STT request error: {e}")
            return None, None
