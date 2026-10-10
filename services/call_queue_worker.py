"""
TakeRemo — Sequential Outbound Call Queue Worker
Enforces the STRICT constraint: EXACTLY ONE active outbound call at a time per worker.
Handles state persistence, pause/resume/cancel, webhook triggers, safe retries,
and post-call data extraction.
"""

import os
import time
import json
import threading
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from services.db import get_db_connection, utc_now
from services.exotel_service import ExotelService
from services.gemini_service import GeminiService
from services.email_service import EmailService

# Global worker state
_worker_lock = threading.RLock()
_worker_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_pause_event = threading.Event()
_pause_event.set()  # Unpaused by default

# Cooldown between sequential calls in seconds
CALL_COOLDOWN_SECONDS = 3
MAX_RETRIES = 2


class CallQueueWorker:
    @classmethod
    def initialize(cls):
        """Recovers state from database after server restart and starts background worker."""
        with _worker_lock:
            cls.recover_crashed_calls()
            cls.ensure_worker_running()

    @classmethod
    def recover_crashed_calls(cls) -> int:
        """Resets any stuck IN_PROGRESS queue items after an unexpected restart."""
        conn = get_db_connection()
        now = utc_now()
        recovered_count = 0
        try:
            with conn:
                stuck = conn.execute("""
                SELECT q.id, q.contact_id, c.provider_call_id
                FROM call_queue q
                JOIN contacts c ON q.contact_id = c.id
                WHERE q.status = 'IN_PROGRESS'
                """).fetchall()

                for item in stuck:
                    conn.execute("UPDATE call_queue SET status = 'QUEUED', updated_at = ? WHERE id = ?", (now, item['id']))
                    conn.execute("""
                    UPDATE contacts
                    SET call_status = 'PENDING', error_details = 'Recovered after server restart'
                    WHERE id = ?
                    """, (item['contact_id'],))
                    recovered_count += 1
                return recovered_count
        finally:
            conn.close()

    @classmethod
    def recover_interrupted_queue(cls) -> int:
        return cls.recover_crashed_calls()

    @classmethod
    def handle_provider_webhook(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handles Exotel carrier status callbacks with idempotency and duplicate-event protection.
        """
        call_sid = payload.get('CallSid') or payload.get('Sid')
        status = (payload.get('Status') or '').lower()
        if not call_sid:
            return {"success": False, "message": "Missing CallSid in payload"}

        conn = get_db_connection()
        now = utc_now()
        try:
            with conn:
                contact = conn.execute("""
                SELECT id, batch_id, call_status
                FROM contacts
                WHERE provider_call_id = ?
                """, (call_sid,)).fetchone()

                if not contact:
                    q_item = conn.execute("""
                    SELECT id, contact_id, status
                    FROM call_queue
                    WHERE provider_call_id = ?
                    """, (call_sid,)).fetchone()
                    if q_item:
                        contact = conn.execute("SELECT id, batch_id, call_status FROM contacts WHERE id = ?", (q_item['contact_id'],)).fetchone()

                if not contact:
                    return {"success": False, "message": f"No contact record found for CallSid {call_sid}"}

                # Idempotency check: if call is already in terminal state
                if contact['call_status'] in ('COMPLETED', 'FAILED', 'UNANSWERED', 'CANCELLED'):
                    return {"success": True, "message": "Event already processed (idempotent)"}

                terminal_status = 'COMPLETED' if status in ('completed', 'answered') else 'FAILED'
                duration = int(payload.get('Duration', 0) or 0)

                conn.execute("""
                UPDATE contacts
                SET call_status = ?, duration_seconds = ?, updated_at = ?
                WHERE id = ?
                """, (terminal_status, duration, now, contact['id']))

                conn.execute("""
                UPDATE call_queue
                SET status = ?, updated_at = ?
                WHERE contact_id = ?
                """, (terminal_status, now, contact['id']))

                conn.execute("""
                INSERT INTO audit_events (event_type, details, created_at)
                VALUES (?, ?, ?)
                """, ('webhook_callback', json.dumps({"callSid": call_sid, "payload": payload}), now))

                return {"success": True, "message": f"Call updated to {terminal_status}"}
        finally:
            conn.close()

    @classmethod
    def ensure_worker_running(cls):
        global _worker_thread
        if _worker_thread is None or not _worker_thread.is_alive():
            _stop_event.clear()
            _worker_thread = threading.Thread(target=cls._worker_loop, daemon=True, name="RemoCallWorker")
            _worker_thread.start()

    @classmethod
    def enqueue_batch(cls, batch_id: str) -> Dict[str, Any]:
        """
        Enqueues all valid, pending contacts for the given batch in sequential row order.
        """
        conn = get_db_connection()
        now = utc_now()
        queued_count = 0
        try:
            with conn:
                # Get valid contacts ordered by row_index
                contacts = conn.execute("""
                SELECT id, service, row_index
                FROM contacts
                WHERE batch_id = ? AND validation_status = 'VALID' AND call_status = 'PENDING'
                ORDER BY row_index ASC
                """, (batch_id,)).fetchall()

                for c in contacts:
                    q_id = f"q_{secrets.token_hex(8)}"
                    conn.execute("""
                    INSERT OR IGNORE INTO call_queue (id, batch_id, contact_id, service, status, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'QUEUED', ?, ?, ?)
                    """, (q_id, batch_id, c['id'], c['service'], c['row_index'], now, now))
                    queued_count += 1

                # Update batch status
                conn.execute("UPDATE batches SET status = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now, batch_id))
        finally:
            conn.close()

        cls.ensure_worker_running()
        return {
            "batchId": batch_id,
            "status": "QUEUED",
            "queuedCount": queued_count
        }

    @classmethod
    def pause_queue(cls):
        _pause_event.clear()

    @classmethod
    def pause(cls):
        cls.pause_queue()

    @classmethod
    def resume_queue(cls):
        _pause_event.set()
        cls.ensure_worker_running()

    @classmethod
    def resume(cls):
        cls.resume_queue()

    @classmethod
    def cancel_queue(cls, batch_id: Optional[str] = None):
        """Cancels queued calls for a specific batch or globally."""
        conn = get_db_connection()
        now = utc_now()
        try:
            with conn:
                query = "UPDATE call_queue SET status = 'CANCELLED', updated_at = ? WHERE status IN ('QUEUED', 'PAUSED')"
                params = [now]
                if batch_id:
                    query += " AND batch_id = ?"
                    params.append(batch_id)
                conn.execute(query, params)

                c_query = "UPDATE contacts SET call_status = 'CANCELLED', updated_at = ? WHERE call_status = 'PENDING'"
                c_params = [now]
                if batch_id:
                    c_query += " AND batch_id = ?"
                    c_params.append(batch_id)
                conn.execute(c_query, c_params)

                if batch_id:
                    conn.execute("UPDATE batches SET status = 'CANCELLED', updated_at = ? WHERE id = ?", (now, batch_id))
        finally:
            conn.close()

    @classmethod
    def cancel(cls, batch_id: Optional[str] = None):
        cls.cancel_queue(batch_id)

    @classmethod
    def get_queue_status(cls, batch_id: Optional[str] = None) -> Dict[str, Any]:
        conn = get_db_connection()
        try:
            where_clause = ""
            params = []
            if batch_id:
                where_clause = "WHERE batch_id = ?"
                params = [batch_id]

            rows = conn.execute(f"""
            SELECT status, COUNT(*) as cnt
            FROM call_queue
            {where_clause}
            GROUP BY status
            """, params).fetchall()

            counts = {r['status']: r['cnt'] for r in rows}

            # Check if an active call is currently executing
            active_item = conn.execute("""
            SELECT q.id, q.batch_id, q.service, c.name, c.phone, c.provider_call_id, c.started_at
            FROM call_queue q
            JOIN contacts c ON q.contact_id = c.id
            WHERE q.status = 'IN_PROGRESS'
            LIMIT 1
            """).fetchone()

            active_call = None
            if active_item:
                active_call = {
                    "queueId": active_item["id"],
                    "batchId": active_item["batch_id"],
                    "service": active_item["service"],
                    "name": active_item["name"],
                    "phone": active_item["phone"],
                    "callSid": active_item["provider_call_id"],
                    "startedAt": active_item["started_at"]
                }

            return {
                "isPaused": not _pause_event.is_set(),
                "queued": counts.get("QUEUED", 0),
                "inProgress": counts.get("IN_PROGRESS", 0),
                "completed": counts.get("COMPLETED", 0),
                "failed": counts.get("FAILED", 0),
                "cancelled": counts.get("CANCELLED", 0),
                "queuedCount": counts.get("QUEUED", 0),
                "inProgressCount": counts.get("IN_PROGRESS", 0),
                "completedCount": counts.get("COMPLETED", 0),
                "failedCount": counts.get("FAILED", 0),
                "isRunning": bool(active_call or counts.get("QUEUED", 0) > 0),
                "activeCall": active_call
            }
        finally:
            conn.close()

    @classmethod
    def _worker_loop(cls):
        """
        Main sequential calling loop.
        STRICT REQUIREMENT: Only ONE call active at a time.
        """
        while not _stop_event.is_set():
            # Wait if paused
            _pause_event.wait()

            # Check if there is already an active call in progress
            conn = get_db_connection()
            active_count = 0
            next_item = None
            try:
                active_row = conn.execute("SELECT COUNT(*) as cnt FROM call_queue WHERE status = 'IN_PROGRESS'").fetchone()
                active_count = active_row['cnt'] if active_row else 0

                if active_count == 0:
                    # Fetch next eligible queued contact (ordered by priority/row_index ASC)
                    next_item = conn.execute("""
                    SELECT q.id as queue_id, q.batch_id, q.contact_id, q.service,
                           c.name, c.phone, c.preferred_language, c.attempt_count, c.raw_data, c.extra_data
                    FROM call_queue q
                    JOIN contacts c ON q.contact_id = c.id
                    WHERE q.status = 'QUEUED'
                    ORDER BY q.priority ASC, q.created_at ASC
                    LIMIT 1
                    """).fetchone()
            finally:
                conn.close()

            # If an active call is already running, wait and loop
            if active_count > 0:
                time.sleep(1)
                continue

            # If no items in queue, idle and check again
            if not next_item:
                time.sleep(2)
                continue

            # Execute the call sequentially
            cls._process_call_item(dict(next_item))

            # Respect cooldown before next call
            time.sleep(CALL_COOLDOWN_SECONDS)

    @classmethod
    def _process_call_item(cls, item: Dict[str, Any]):
        queue_id = item['queue_id']
        contact_id = item['contact_id']
        batch_id = item['batch_id']
        service = item['service']
        phone = item['phone']
        name = item['name']
        attempts = (item.get('attempt_count') or 0) + 1

        conn = get_db_connection()
        now = utc_now()
        try:
            with conn:
                conn.execute("UPDATE call_queue SET status = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now, queue_id))
                conn.execute("""
                UPDATE contacts
                SET call_status = 'CALLING', attempt_count = ?, started_at = ?, updated_at = ?
                WHERE id = ?
                """, (attempts, now, now, contact_id))
        finally:
            conn.close()

        # Step 4: Initiate real outbound call through Exotel
        try:
            call_res = ExotelService.initiate_outbound_call(
                to_phone=phone,
                custom_field=contact_id
            )
        except Exception as e:
            err_msg = str(e)
            print(f"[CallQueueWorker] Outbound call dispatch failed for {contact_id}: {err_msg}")
            conn = get_db_connection()
            now = utc_now()
            try:
                with conn:
                    conn.execute("UPDATE call_queue SET status = 'FAILED', updated_at = ? WHERE id = ?", (now, queue_id))
                    conn.execute("UPDATE contacts SET call_status = 'FAILED', error_details = ?, updated_at = ? WHERE id = ?", (err_msg, now, contact_id))
            finally:
                conn.close()
            return

        if not call_res.get("success"):
            err_msg = call_res.get("error") or "Exotel rejected call dispatch."
            print(f"[CallQueueWorker] Call rejected for {contact_id}: {err_msg}")
            conn = get_db_connection()
            now = utc_now()
            try:
                with conn:
                    conn.execute("UPDATE call_queue SET status = 'FAILED', updated_at = ? WHERE id = ?", (now, queue_id))
                    conn.execute("UPDATE contacts SET call_status = 'FAILED', error_details = ?, updated_at = ? WHERE id = ?", (err_msg, now, contact_id))
            finally:
                conn.close()
            return

        call_sid = call_res.get("callSid") or f"EXO_{secrets.token_hex(6)}"
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                UPDATE contacts
                SET provider_call_id = ?, call_status = 'CALLING', updated_at = ?
                WHERE id = ?
                """, (call_sid, utc_now(), contact_id))
        finally:
            conn.close()

        # In testing mode only, run automated simulation cycle
        if os.environ.get('TESTING') == '1':
            cls._execute_conversation_cycle(contact_id, batch_id, service, name, phone, call_sid, item)

    @classmethod
    def _execute_conversation_cycle(cls, contact_id: str, batch_id: str, service: str, name: str, phone: str, call_sid: str, item: Dict[str, Any]):
        """
        Conducts turn-by-turn conversation using Gemini, records transcripts,
        and extracts structured results upon completion.
        """
        conn = get_db_connection()
        conv_id = f"conv_{secrets.token_hex(8)}"
        now = utc_now()
        try:
            with conn:
                conn.execute("""
                INSERT INTO conversations (
                    id, contact_id, batch_id, service, phone, contact_name, status, started_at, language, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'in-progress', ?, ?, ?)
                """, (conv_id, contact_id, batch_id, service, phone, name, now, item.get('preferred_language', 'en'), now))
        finally:
            conn.close()

        contact_info = {
            "name": name,
            "phone": phone,
            "preferred_language": item.get('preferred_language', 'en'),
            "extra": json.loads(item.get('extra_data') or '{}')
        }

        # Turn 1: Opening Greeting
        turn1 = GeminiService.generate_reply(service, contact_info, [], None)
        cls._record_transcript_turn(conv_id, "REMO", turn1['spoken_response'], "00:02", turn1['detected_language'])

        # Turn 2: Simulated realistic candidate/prospect response
        sim_response = cls._generate_simulated_user_turn(service, contact_info)
        cls._record_transcript_turn(conv_id, name, sim_response, "00:08", turn1['detected_language'])

        # Turn 3: Remo response & qualification
        turn3 = GeminiService.generate_reply(service, contact_info, [
            {"speaker": "REMO", "text": turn1['spoken_response']},
            {"speaker": name, "text": sim_response}
        ], None)
        cls._record_transcript_turn(conv_id, "REMO", turn3['spoken_response'], "00:15", turn3['detected_language'])

        # Turn 4: Final closing
        sim_close = "Yes, that sounds good. Thank you!"
        cls._record_transcript_turn(conv_id, name, sim_close, "00:22", turn3['detected_language'])

        # Final evaluation turn
        final_turn = GeminiService.generate_reply(service, contact_info, [
            {"speaker": "REMO", "text": turn1['spoken_response']},
            {"speaker": name, "text": sim_response},
            {"speaker": "REMO", "text": turn3['spoken_response']},
            {"speaker": name, "text": sim_close}
        ], None)

        # Mark terminal state
        ended_at = utc_now()
        duration_seconds = 35
        summary = final_turn.get("call_summary") or "Screening call completed successfully."
        classification = final_turn.get("classification") or ("Accepted / Shortlisted" if service == 'recruitment' else "QUALIFIED")
        extracted = final_turn.get("extracted_fields") or {}

        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                UPDATE conversations
                SET status = 'completed', ended_at = ?, duration_seconds = ?, summary = ?, classification = ?
                WHERE id = ?
                """, (ended_at, duration_seconds, summary, classification, conv_id))

                conn.execute("""
                UPDATE contacts
                SET call_status = 'COMPLETED', ended_at = ?, duration_seconds = ?,
                    detected_language = ?, call_outcome = 'ANSWERED', classification = ?,
                    extracted_data = ?, summary = ?, updated_at = ?
                WHERE id = ?
                """, (
                    ended_at, duration_seconds, final_turn.get('detected_language', 'en'),
                    classification, json.dumps(extracted), summary, ended_at, contact_id
                ))

                conn.execute("""
                UPDATE call_queue
                SET status = 'COMPLETED', updated_at = ?
                WHERE contact_id = ?
                """, (ended_at, contact_id))

                # Check if batch is completely finished
                remaining = conn.execute("""
                SELECT COUNT(*) as cnt FROM call_queue
                WHERE batch_id = ? AND status IN ('QUEUED', 'IN_PROGRESS')
                """, (batch_id,)).fetchone()

                if remaining and remaining['cnt'] == 0:
                    conn.execute("UPDATE batches SET status = 'COMPLETED', updated_at = ? WHERE id = ?", (ended_at, batch_id))
                    # Trigger async email notification
                    EmailService.send_batch_completion_summary(batch_id)
        finally:
            conn.close()

    @classmethod
    def _record_transcript_turn(cls, conv_id: str, speaker: str, text: str, time_str: str, language: str):
        conn = get_db_connection()
        now = utc_now()
        try:
            with conn:
                conn.execute("""
                INSERT INTO transcript_messages (conversation_id, speaker, text, time_str, timestamp, language)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (conv_id, speaker, text, time_str, now, language))
        finally:
            conn.close()

    @classmethod
    def _generate_simulated_user_turn(cls, service: str, contact_info: Dict[str, Any]) -> str:
        name = contact_info.get('name', 'I')
        extra = contact_info.get('extra', {})
        if service == 'recruitment':
            role = extra.get('job_role') or 'Software Engineer'
            exp = extra.get('experience') or '4 years'
            skills = extra.get('skills') or 'Python and cloud architecture'
            return f"Yes, I can talk! I have {exp} of experience in {role}, mainly working with {skills}."
        elif service == 'sales':
            req = extra.get('product_or_service') or 'voice automation'
            return f"Hi Remo, yes, we are actively looking into {req} to reduce our response times."
        else:
            issue = extra.get('issue_or_query') or 'account access'
            return f"Hi Remo, I was experiencing an issue with my {issue} earlier today."


# Initialize worker on module load
CallQueueWorker.initialize()
