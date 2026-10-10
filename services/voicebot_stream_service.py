"""
TakeRemo — Real-Time Voicebot WebSocket Handler (Exotel AgentStream Protocol)
Handles bidirectional audio streaming between Exotel and Sarvam AI / Gemini.
Audio format: Linear PCM 16-bit 8000Hz mono.
"""

import os
import io
import json
import wave
import math
import struct
import base64
import time
import asyncio
from typing import Optional, Dict, Any, List

from starlette.websockets import WebSocket, WebSocketDisconnect
from services.sarvam_service import SarvamService
from services.gemini_service import GeminiService
from services.db import get_db_connection, utc_now
import secrets


def calculate_rms(pcm_bytes: bytes) -> float:
    """Calculates RMS audio energy of 16-bit PCM bytes."""
    if not pcm_bytes:
        return 0.0
    count = len(pcm_bytes) // 2
    if count == 0:
        return 0.0
    shorts = struct.unpack(f"<{count}h", pcm_bytes[:count * 2])
    sum_sq = sum(s * s for s in shorts)
    return math.sqrt(sum_sq / count)


async def handle_voicebot_websocket(websocket: WebSocket):
    await websocket.accept()
    print("[VoicebotStream] Exotel WebSocket connection accepted.")

    stream_sid: Optional[str] = None
    call_sid: Optional[str] = None
    custom_field: Optional[str] = None
    contact_id: Optional[str] = None
    contact_name = "Candidate"
    service = "recruitment"
    conv_id: Optional[str] = None

    audio_buffer = bytearray()
    speech_detected = False
    silence_frames = 0
    ENERGY_THRESHOLD = 350.0  # Threshold for voice activity
    SILENCE_LIMIT_FRAMES = 18  # ~18 chunks of 100ms = ~1.8 seconds of silence to finalize turn
    is_processing_turn = False
    conversation_history: List[Dict[str, str]] = []

    try:
        while True:
            message_text = await websocket.receive_text()
            data = json.loads(message_text)
            event = data.get("event")

            if event == "connected":
                print("[VoicebotStream] Event: CONNECTED")

            elif event == "start":
                start_info = data.get("start", {})
                stream_sid = data.get("stream_sid") or start_info.get("stream_sid")
                call_sid = start_info.get("call_sid")
                custom_field = start_info.get("custom_field")
                contact_id = custom_field
                print(f"[VoicebotStream] Event: START stream_sid={stream_sid}, call_sid={call_sid}, contact_id={contact_id}")

                # Find contact in DB if custom_field exists
                if contact_id:
                    conn = get_db_connection()
                    try:
                        row = conn.execute("SELECT name, service FROM contacts WHERE id = ?", (contact_id,)).fetchone()
                        if row:
                            contact_name = row['name'] or "Candidate"
                            service = row['service'] or "recruitment"
                    except Exception as e:
                        print(f"[VoicebotStream] DB lookup notice: {e}")
                    finally:
                        conn.close()

                # Initialize conversation record in DB
                conv_id = f"conv_{secrets.token_hex(8)}"
                now = utc_now()
                conn = get_db_connection()
                try:
                    with conn:
                        conn.execute("""
                        INSERT INTO conversations (
                            id, contact_id, batch_id, service, phone, contact_name, status, started_at, language, created_at
                        ) VALUES (?, ?, 'live_stream', ?, '', ?, 'in-progress', ?, 'en', ?)
                        """, (conv_id, contact_id or f"cnt_{secrets.token_hex(4)}", service, contact_name, now, now))

                        # Log Remo's greeting
                        conn.execute("""
                        INSERT INTO transcript_messages (conversation_id, speaker, text, time_str, timestamp, language)
                        VALUES (?, 'REMO', 'Hey, it''s Remo, representing Score Labs.', '00:02', ?, 'en')
                        """, (conv_id, now))
                except Exception as e:
                    print(f"[VoicebotStream] Conv init error: {e}")
                finally:
                    conn.close()

                conversation_history.append({"speaker": "REMO", "text": "Hey, it's Remo, representing Score Labs."})

            elif event == "media":
                if is_processing_turn or not stream_sid:
                    continue

                media_info = data.get("media", {})
                payload_b64 = media_info.get("payload")
                if not payload_b64:
                    continue

                try:
                    raw_pcm = base64.b64decode(payload_b64)
                except Exception:
                    continue

                energy = calculate_rms(raw_pcm)

                if energy > ENERGY_THRESHOLD:
                    speech_detected = True
                    silence_frames = 0
                    audio_buffer.extend(raw_pcm)
                elif speech_detected:
                    audio_buffer.extend(raw_pcm)
                    silence_frames += 1

                    # Caller paused long enough -> Process speech turn!
                    if silence_frames >= SILENCE_LIMIT_FRAMES and len(audio_buffer) >= 16000:
                        is_processing_turn = True
                        pcm_to_process = bytes(audio_buffer)
                        audio_buffer.clear()
                        speech_detected = False
                        silence_frames = 0

                        # Run transcription and reply in background task
                        asyncio.create_task(
                            _process_caller_speech(
                                websocket,
                                stream_sid,
                                pcm_to_process,
                                conv_id,
                                contact_name,
                                service,
                                conversation_history
                            )
                        )
                        is_processing_turn = False

            elif event == "stop":
                print(f"[VoicebotStream] Event: STOP stream_sid={stream_sid}")
                if conv_id:
                    now = utc_now()
                    conn = get_db_connection()
                    try:
                        with conn:
                            conn.execute("UPDATE conversations SET status = 'completed', ended_at = ? WHERE id = ?", (now, conv_id))
                    except Exception:
                        pass
                    finally:
                        conn.close()
                break

    except WebSocketDisconnect:
        print("[VoicebotStream] Exotel WebSocket disconnected normally.")
    except Exception as e:
        print(f"[VoicebotStream] WebSocket stream error: {e}")


async def _process_caller_speech(
    websocket: WebSocket,
    stream_sid: str,
    pcm_bytes: bytes,
    conv_id: Optional[str],
    contact_name: str,
    service: str,
    conversation_history: List[Dict[str, str]]
):
    """Transcribes audio with Sarvam STT, generates reply with Gemini, and streams Sarvam TTS audio back."""
    try:
        # 1. Package PCM 8000Hz into WAV container for Sarvam STT
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(8000)
            wav_file.writeframes(pcm_bytes)
        wav_bytes = buf.getvalue()

        loop = asyncio.get_running_loop()
        transcript, lang = await loop.run_in_executor(
            None,
            lambda: SarvamService.speech_to_text(wav_bytes, filename="user_turn.wav")
        )

        if not transcript or not transcript.strip():
            print("[VoicebotStream] No recognizable speech detected.")
            return

        print(f"[VoicebotStream] >>> Caller ({contact_name}): {transcript}")
        detected_lang = lang or "en"

        # Record user turn in DB
        now = utc_now()
        if conv_id:
            conn = get_db_connection()
            try:
                with conn:
                    conn.execute("""
                    INSERT INTO transcript_messages (conversation_id, speaker, text, time_str, timestamp, language)
                    VALUES (?, ?, ?, 'turn', ?, ?)
                    """, (conv_id, contact_name, transcript, now, detected_lang))
            except Exception as e:
                print(f"[VoicebotStream] Error recording user turn: {e}")
            finally:
                conn.close()

        conversation_history.append({"speaker": contact_name, "text": transcript})

        # 2. Generate intelligent response using Gemini
        contact_info = {"name": contact_name, "phone": "", "preferred_language": detected_lang}
        gemini_res = await loop.run_in_executor(
            None,
            lambda: GeminiService.generate_reply(service, contact_info, conversation_history, transcript)
        )
        reply_text = gemini_res.get('spoken_response') or "Thank you. Let me make a note of that for our team."
        print(f"[VoicebotStream] <<< Remo Response: {reply_text}")

        # Record Remo turn in DB
        if conv_id:
            conn = get_db_connection()
            try:
                with conn:
                    conn.execute("""
                    INSERT INTO transcript_messages (conversation_id, speaker, text, time_str, timestamp, language)
                    VALUES (?, 'REMO', ?, 'turn', ?, ?)
                    """, (conv_id, reply_text, now, detected_lang))
            except Exception:
                pass
            finally:
                conn.close()

        conversation_history.append({"speaker": "REMO", "text": reply_text})

        # 3. Generate Speech with Sarvam TTS
        audio_b64 = await loop.run_in_executor(
            None,
            lambda: SarvamService.text_to_speech(reply_text, language=detected_lang)
        )

        if not audio_b64:
            print("[VoicebotStream] Failed to generate TTS audio.")
            return

        # Decode audio and resample to 8000Hz 16-bit PCM for Exotel
        full_audio_bytes = base64.b64decode(audio_b64)
        try:
            import audioop
            buf = io.BytesIO(full_audio_bytes)
            with wave.open(buf, 'rb') as w:
                frames = w.readframes(w.getnframes())
                framerate = w.getframerate()
                if framerate != 8000:
                    pcm_out, _ = audioop.ratecv(frames, 2, 1, framerate, 8000, None)
                else:
                    pcm_out = frames
        except Exception as e:
            print(f"[VoicebotStream] Warning: Audio resampling failed ({e}). Using raw bytes.")
            pcm_out = full_audio_bytes[44:] if len(full_audio_bytes) > 44 else full_audio_bytes

        # 4. Stream PCM chunks (~3200 bytes = 200ms) to Exotel over WebSocket
        chunk_size = 3200
        start_time = time.time()
        for i in range(0, len(pcm_out), chunk_size):
            chunk = pcm_out[i:i + chunk_size]
            chunk_b64 = base64.b64encode(chunk).decode('ascii')
            media_msg = {
                "event": "media",
                "stream_sid": stream_sid,
                "media": {
                    "payload": chunk_b64
                }
            }
            await websocket.send_text(json.dumps(media_msg))
            expected_time = start_time + (i + chunk_size) / 16000.0
            sleep_time = expected_time - time.time()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

    except Exception as e:
        print(f"[VoicebotStream] Error processing caller speech turn: {e}")
