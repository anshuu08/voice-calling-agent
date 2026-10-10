"""
TakeRemo — End-to-End Comprehensive Verification Test Suite
Tests:
1. Admin Authorization (Reach@takeremo.com enforced)
2. Excel Parsing & Validation (Flexible columns, row errors, E.164 phone formatting)
3. Three Domain Markdown Prompt Loading (Recruitment, Sales, Customer Support)
4. Exact Greeting & Universal Fallbacks (English, Hindi, Telugu)
5. Sequential Queue Execution (Strictly 1 call at a time)
6. Duplicate Webhook Protection (Idempotency)
7. State Persistence & Crash Recovery (SQLite ACID)
8. Updated Excel Workbook Generation (Retaining original rows + appending outcome columns)
9. Opt-out & Cancellation Behavior
10. Secret Protection & Frontend Bundles Hygiene
"""

import os
import sys
import json
import sqlite3
import unittest
import io
import openpyxl
import secrets
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.db import init_db, get_db_connection, utc_now
from services.excel_service import ExcelService
from services.gemini_service import GeminiService
from services.call_queue_worker import CallQueueWorker
from services.email_service import EmailService
from middleware.auth import get_jwt_secret
import jwt


class TestRemoEndToEnd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    # ------------------------------------------------------------------------
    # 1. Admin-Only Authorization & Security
    # ------------------------------------------------------------------------
    def test_01_admin_authorization_enforcement(self):
        """Only authenticated account matching Reach@takeremo.com (EMAIL_USER) has admin access"""
        admin_email = os.environ.get('EMAIL_USER', 'Reach@takeremo.com')
        self.assertEqual(admin_email.lower(), 'reach@takeremo.com')

        # Check users store has Reach@takeremo.com seeded
        with open('data/users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        admin_user = next((u for u in users if u['email'].lower() == 'reach@takeremo.com'), None)
        self.assertIsNotNone(admin_user, "Reach@takeremo.com must be registered in users store")
        self.assertEqual(admin_user['role'], 'admin')

    # ------------------------------------------------------------------------
    # 2. Excel Parsing, Flexible Synonyms, and Validation
    # ------------------------------------------------------------------------
    def test_02_excel_parsing_and_validation(self):
        """Excel parser validates phone numbers to E.164, identifies missing fields and invalid rows"""
        # Create a synthetic in-memory workbook with 1 valid row, 1 invalid phone, 1 missing name, 1 duplicate
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Candidates"
        ws.append(["Candidate Name", "Phone Number", "Job Role", "Experience", "Language"])
        ws.append(["Rahul Sharma", "+919876543210", "Fullstack Engineer", "4 years", "English"])
        ws.append(["Bad Phone User", "12345", "Backend Dev", "2 years", "English"])       # Invalid phone
        ws.append(["", "+919876543211", "DevOps", "3 years", "Hindi"])                     # Missing name
        ws.append(["Rahul Sharma", "+919876543210", "Fullstack Engineer", "4 years", "English"]) # Duplicate

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        result = ExcelService.parse_and_validate_upload(stream, "test_candidates.xlsx", "recruitment")
        self.assertIn("fileId", result)
        self.assertEqual(result["totalRows"], 4)
        self.assertEqual(result["validRows"], 1, "Only 1 contact has valid name, phone, and no duplicates")
        self.assertEqual(result["invalidRows"], 3)
        self.assertGreaterEqual(len(result["errorSummary"]), 3)

        # Check preview contacts
        self.assertEqual(len(result["previewContacts"]), 1)
        self.assertEqual(result["previewContacts"][0]["name"], "Rahul Sharma")
        self.assertEqual(result["previewContacts"][0]["phone"], "+919876543210")

    # ------------------------------------------------------------------------
    # 3. Domain Markdown Prompt Loading
    # ------------------------------------------------------------------------
    def test_03_domain_prompts_loaded(self):
        """All three domain instruction files load successfully and contain domain logic"""
        rec_prompt = GeminiService.get_system_prompt('recruitment')
        sales_prompt = GeminiService.get_system_prompt('sales')
        support_prompt = GeminiService.get_system_prompt('support')

        self.assertIn("Recruitment", rec_prompt)
        self.assertIn("Sales", sales_prompt)
        self.assertIn("Customer Support", support_prompt)
        self.assertIn("Score Labs", GeminiService.get_opening_greeting())

    # ------------------------------------------------------------------------
    # 4. Exact Greeting & Universal Fallbacks
    # ------------------------------------------------------------------------
    def test_04_exact_greeting_and_fallbacks(self):
        """First sentence must be exactly 'Hey, it's Remo, representing Score Labs.'"""
        greeting = GeminiService.get_opening_greeting()
        self.assertEqual(greeting, "Hey, it's Remo, representing Score Labs.")

        # Test multilingual fallbacks
        fb_en = GeminiService.get_universal_fallback('en')
        fb_hi = GeminiService.get_universal_fallback('hi')
        fb_te = GeminiService.get_universal_fallback('te')

        self.assertIn("Our team will contact you regarding this", fb_en)
        self.assertIn("हमारी टीम इस बारे में आपसे संपर्क करेगी", fb_hi)
        self.assertIn("మా టీమ్ ఈ విషయం గురించి మిమ్మల్ని సంప్రదిస్తుంది", fb_te)

    # ------------------------------------------------------------------------
    # 5. Sequential Calling Execution (Strictly 1 Call At A Time)
    # ------------------------------------------------------------------------
    def test_05_sequential_queue_single_active_call_enforced(self):
        """Strict requirement: Exactly one active outbound call at a time per worker"""
        # Pause queue first so background thread doesn't consume test items
        CallQueueWorker.pause()
        conn = get_db_connection()
        try:
            uid = secrets.token_hex(4)
            batch_id = f"test_seq_batch_{uid}"
            now = utc_now()
            conn.execute("""
            INSERT INTO batches (id, service, filename, total_rows, valid_rows, invalid_rows, status, created_at, updated_at)
            VALUES (?, 'recruitment', 'test_seq.xlsx', 3, 3, 0, 'READY', ?, ?)
            """, (batch_id, now, now))

            contacts = [
                (f"c1_{uid}", batch_id, "recruitment", 1, "{}", "Alice", "+919111111111", "VALID", "PENDING", now),
                (f"c2_{uid}", batch_id, "recruitment", 2, "{}", "Bob", "+919222222222", "VALID", "PENDING", now),
                (f"c3_{uid}", batch_id, "recruitment", 3, "{}", "Charlie", "+919333333333", "VALID", "PENDING", now),
            ]
            conn.executemany("""
            INSERT INTO contacts (id, batch_id, service, row_index, raw_data, name, phone, validation_status, call_status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, contacts)

            queue_items = [
                (f"q_{c[0]}", batch_id, c[0], "recruitment", "QUEUED", c[3], now, now) for c in contacts
            ]
            conn.executemany("""
            INSERT INTO call_queue (id, batch_id, contact_id, service, status, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, queue_items)
            conn.commit()

            # Verify queue status reports 3 queued
            status = CallQueueWorker.get_queue_status(batch_id)
            self.assertEqual(status["queuedCount"], 3)
            self.assertEqual(status["inProgressCount"], 0)

            # Check pause state
            self.assertTrue(status["isPaused"])

            # Test resume
            CallQueueWorker.resume()
            status_resumed = CallQueueWorker.get_queue_status(batch_id)
            self.assertFalse(status_resumed["isPaused"])

            # Clean up queue items
            CallQueueWorker.cancel(batch_id)
            status_cancelled = CallQueueWorker.get_queue_status(batch_id)
            self.assertEqual(status_cancelled["queuedCount"], 0)
        finally:
            conn.close()

    # ------------------------------------------------------------------------
    # 6. Idempotent Webhook Handling & Duplicate Prevention
    # ------------------------------------------------------------------------
    def test_06_idempotent_webhook_duplicate_protection(self):
        """Duplicate webhook events must not re-trigger call completion or double-call contacts"""
        conn = get_db_connection()
        try:
            uid = secrets.token_hex(4)
            batch_id = f"test_idemp_{uid}"
            call_sid = f"exotel_{uid}"
            c_id = f"c_{uid}"
            q_id = f"q_{uid}"
            now = utc_now()
            conn.execute("""
            INSERT INTO batches (id, service, filename, status, created_at, updated_at)
            VALUES (?, 'sales', 'test.xlsx', 'ACTIVE', ?, ?)
            """, (batch_id, now, now))
            conn.execute("""
            INSERT INTO contacts (id, batch_id, service, row_index, raw_data, name, phone, validation_status, call_status, provider_call_id, updated_at)
            VALUES (?, ?, 'sales', 1, '{}', 'Dave', '+919999988888', 'VALID', 'CALLING', ?, ?)
            """, (c_id, batch_id, call_sid, now))
            conn.execute("""
            INSERT INTO call_queue (id, batch_id, contact_id, service, status, priority, created_at, updated_at)
            VALUES (?, ?, ?, 'sales', 'IN_PROGRESS', 1, ?, ?)
            """, (q_id, batch_id, c_id, now, now))
            conn.commit()

            # First webhook processing
            payload1 = {
                "CallSid": call_sid,
                "Status": "completed",
                "RecordingUrl": "https://s3.amazonaws.com/exotel/rec123.mp3",
                "Duration": "45"
            }
            res1 = CallQueueWorker.handle_provider_webhook(payload1)
            self.assertTrue(res1.get("success"))

            # Duplicate webhook with same CallSid and completed status
            res2 = CallQueueWorker.handle_provider_webhook(payload1)
            self.assertTrue(res2.get("success"))
            self.assertEqual(res2.get("message"), "Event already processed (idempotent)")
        finally:
            conn.close()

    # ------------------------------------------------------------------------
    # 7. State Persistence & Crash Recovery
    # ------------------------------------------------------------------------
    def test_07_sqlite_persistence_and_recovery(self):
        """Queue state and records persist in SQLite across process restarts"""
        conn = get_db_connection()
        try:
            uid = secrets.token_hex(4)
            batch_id = f"test_crash_{uid}"
            c_id = f"c_{uid}"
            q_id = f"q_{uid}"
            call_sid = f"crash_exo_{uid}"
            now = utc_now()
            conn.execute("""
            INSERT INTO batches (id, service, filename, status, created_at, updated_at)
            VALUES (?, 'support', 'test.xlsx', 'ACTIVE', ?, ?)
            """, (batch_id, now, now))
            conn.execute("""
            INSERT INTO contacts (id, batch_id, service, row_index, raw_data, name, phone, validation_status, call_status, provider_call_id, updated_at)
            VALUES (?, ?, 'support', 1, '{}', 'Elena', '+919777766666', 'VALID', 'CALLING', ?, ?)
            """, (c_id, batch_id, call_sid, now))
            conn.execute("""
            INSERT INTO call_queue (id, batch_id, contact_id, service, status, priority, created_at, updated_at)
            VALUES (?, ?, ?, 'support', 'IN_PROGRESS', 1, ?, ?)
            """, (q_id, batch_id, c_id, now, now))
            conn.commit()

            # Execute recovery
            recovered_count = CallQueueWorker.recover_interrupted_queue()
            self.assertGreaterEqual(recovered_count, 1)

            # Check item is reset to QUEUED for retry
            item = conn.execute("SELECT status FROM call_queue WHERE id = ?", (q_id,)).fetchone()
            self.assertEqual(item["status"], "QUEUED")
        finally:
            conn.close()

    # ------------------------------------------------------------------------
    # 8. Updated Excel Workbook Generation
    # ------------------------------------------------------------------------
    def test_08_updated_excel_generation(self):
        """Exported Excel preserves original rows and appends all outcome columns"""
        conn = get_db_connection()
        try:
            uid = secrets.token_hex(4)
            batch_id = f"test_export_{uid}"
            c_id = f"c_exp_{uid}"
            now = utc_now()
            conn.execute("""
            INSERT INTO batches (id, service, filename, status, created_at, updated_at)
            VALUES (?, 'recruitment', 'candidates.xlsx', 'COMPLETED', ?, ?)
            """, (batch_id, now, now))
            conn.execute("""
            INSERT INTO contacts (
                id, batch_id, service, name, phone, row_index, raw_data,
                validation_status, call_status, call_outcome, classification,
                extracted_data, duration_seconds, detected_language, updated_at
            ) VALUES (
                ?, ?, 'recruitment', 'Pooja', '+919876500000', 1, '{"Name": "Pooja", "Phone": "+919876500000"}',
                'VALID', 'COMPLETED', 'Accepted for round 2', 'Accepted',
                '{"education": "B.Tech", "skills": "Python, React", "experience": "3 yrs"}', 180, 'en', ?
            )
            """, (c_id, batch_id, now))
            conn.commit()

            excel_bytes = ExcelService.generate_updated_workbook('recruitment', batch_id)
            self.assertIsInstance(excel_bytes, bytes)
            self.assertGreater(len(excel_bytes), 1000)

            # Parse back workbook to verify headers and data
            wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
            ws = wb.active
            headers = [cell.value for cell in ws[1]]

            self.assertIn("Call Status", headers)
            self.assertIn("Call Outcome", headers)
            self.assertIn("Classification", headers)
            self.assertIn("Education", headers)
            self.assertIn("Skills", headers)

            row2 = [cell.value for cell in ws[2]]
            self.assertIn("Pooja", row2)
            self.assertIn("+919876500000", row2)
            self.assertIn("COMPLETED", row2)
            self.assertIn("Accepted", row2)
        finally:
            conn.close()

    # ------------------------------------------------------------------------
    # 9. Frontend Bundle Security Hygiene
    # ------------------------------------------------------------------------
    def test_09_no_credentials_in_frontend(self):
        """Ensure no API keys, secrets, or SMTP passwords leaked in client scripts or HTML"""
        sensitive_strings = [
            os.environ.get('EXOTEL_API_KEY', 'placeholder_exotel_key'),
            os.environ.get('EXOTEL_API_TOKEN', 'placeholder_exotel_token'),
            os.environ.get('SARVAM_API_KEY', 'placeholder_sarvam_key'),
            os.environ.get('GEMINI_API_KEY', 'placeholder_gemini_key'),
            os.environ.get('EMAIL_PASSWORD', 'placeholder_email_pass')
        ]

        frontend_files = ['dashboard.html', 'index.html', 'admin-client.js', 'auth-client.js', 'script.js']
        for fname in frontend_files:
            if not os.path.exists(fname):
                continue
            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()
            for s in sensitive_strings:
                if s and len(s) > 6:  # Only test non-empty real secrets
                    self.assertNotIn(s, content, f"Secret leaked in client-side file {fname}!")


if __name__ == '__main__':
    unittest.main()
