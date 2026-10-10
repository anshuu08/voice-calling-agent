"""
TakeRemo — Persistent Database Layer (SQLite)
Provides thread-safe ACID persistence for Batches, Contacts, Queue, Calls, Transcripts, and Audit Events.
Survives application restarts and requires no external database daemon.
"""

import os
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'remo.db')

_lock = threading.RLock()


def get_db_connection() -> sqlite3.Connection:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                # 1. Batches table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS batches (
                    id TEXT PRIMARY KEY,
                    service TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    original_path TEXT,
                    status TEXT NOT NULL DEFAULT 'READY',
                    total_rows INTEGER NOT NULL DEFAULT 0,
                    valid_rows INTEGER NOT NULL DEFAULT 0,
                    invalid_rows INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """)

                # 2. Contacts table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id TEXT PRIMARY KEY,
                    batch_id TEXT NOT NULL,
                    service TEXT NOT NULL,
                    row_index INTEGER NOT NULL,
                    raw_data TEXT NOT NULL,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    preferred_language TEXT DEFAULT 'en',
                    notes TEXT,
                    extra_data TEXT,
                    validation_status TEXT NOT NULL DEFAULT 'VALID',
                    validation_errors TEXT,
                    call_status TEXT NOT NULL DEFAULT 'PENDING',
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    provider_call_id TEXT,
                    started_at TEXT,
                    ended_at TEXT,
                    duration_seconds INTEGER DEFAULT 0,
                    detected_language TEXT,
                    call_outcome TEXT,
                    classification TEXT,
                    extracted_data TEXT,
                    summary TEXT,
                    error_details TEXT,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(batch_id) REFERENCES batches(id)
                )
                """)

                # 3. Call Queue table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS call_queue (
                    id TEXT PRIMARY KEY,
                    batch_id TEXT NOT NULL,
                    contact_id TEXT NOT NULL UNIQUE,
                    service TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'QUEUED',
                    priority INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(batch_id) REFERENCES batches(id),
                    FOREIGN KEY(contact_id) REFERENCES contacts(id)
                )
                """)

                # 4. Conversations table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    contact_id TEXT NOT NULL,
                    batch_id TEXT NOT NULL,
                    service TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    contact_name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'in-progress',
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'en',
                    summary TEXT,
                    classification TEXT,
                    sentiment TEXT DEFAULT 'neutral',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id)
                )
                """)

                # 5. Transcript messages
                conn.execute("""
                CREATE TABLE IF NOT EXISTS transcript_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    speaker TEXT NOT NULL,
                    text TEXT NOT NULL,
                    time_str TEXT,
                    timestamp TEXT NOT NULL,
                    language TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
                """)

                # 6. Audit Events table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT NOT NULL
                )
                """)

                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_batch ON contacts(batch_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_service ON contacts(service)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON call_queue(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_service ON conversations(service)")
        finally:
            conn.close()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# Initialize on import
init_db()
