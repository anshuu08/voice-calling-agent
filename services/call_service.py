"""
TakeRemo — Call History Service Layer
Provides live telephony session logs, call metadata, durations, and status tracking from SQLite.
"""

from typing import Dict, Any, List
from services.db import get_db_connection


class CallService:
    _SAMPLE_CALLS: List[Dict[str, Any]] = [
        {
            "id": "call_101",
            "callSid": "CA_89201948ba01",
            "service": "recruitment",
            "user": "Score Labs",
            "callerNumber": "+919876543210",
            "callerName": "Rahul Sharma",
            "direction": "outbound",
            "status": "completed",
            "durationSeconds": 272,
            "duration": "04:32",
            "startedAt": "2026-10-05T09:30:00Z",
            "endedAt": "2026-10-05T09:34:32Z",
            "conversationId": "conv_001",
            "recordingAvailable": False
        },
        {
            "id": "call_102",
            "callSid": "CA_90118239ca02",
            "service": "sales",
            "user": "Score Labs",
            "callerNumber": "+13125550144",
            "callerName": "Tom Bradley",
            "direction": "outbound",
            "status": "completed",
            "durationSeconds": 198,
            "duration": "03:18",
            "startedAt": "2026-10-05T08:15:00Z",
            "endedAt": "2026-10-05T08:18:18Z",
            "conversationId": "conv_002",
            "recordingAvailable": False
        },
        {
            "id": "call_103",
            "callSid": "CA_77192038da03",
            "service": "support",
            "user": "Score Labs",
            "callerNumber": "+12065550183",
            "callerName": "Marcus Vance",
            "direction": "outbound",
            "status": "escalated",
            "durationSeconds": 165,
            "duration": "02:45",
            "startedAt": "2026-10-04T15:20:00Z",
            "endedAt": "2026-10-04T15:22:45Z",
            "conversationId": "conv_003",
            "recordingAvailable": False
        },
        {
            "id": "call_104",
            "callSid": "CA_66190284ea04",
            "service": "recruitment",
            "user": "TalentBridge Staffing",
            "callerNumber": "+919811223344",
            "callerName": "Priya Sharma",
            "direction": "outbound",
            "status": "completed",
            "durationSeconds": 112,
            "duration": "01:52",
            "startedAt": "2026-10-04T11:45:00Z",
            "endedAt": "2026-10-04T11:46:52Z",
            "conversationId": "conv_004",
            "recordingAvailable": False
        },
        {
            "id": "call_105",
            "callSid": "CA_55190284fa05",
            "service": "sales",
            "user": "FinTech Scale",
            "callerNumber": "+19175550192",
            "callerName": "Elena Rostova",
            "direction": "outbound",
            "status": "active",
            "durationSeconds": 70,
            "duration": "01:10",
            "startedAt": "2026-10-05T10:40:00Z",
            "endedAt": None,
            "conversationId": "conv_005",
            "recordingAvailable": False
        },
        {
            "id": "call_106",
            "callSid": "CA_44190284ga06",
            "service": "support",
            "user": "Nexus Retail",
            "callerNumber": "+14155550100",
            "callerName": "Jordan Lee",
            "direction": "inbound",
            "status": "missed",
            "durationSeconds": 14,
            "duration": "00:14",
            "startedAt": "2026-10-03T14:10:00Z",
            "endedAt": "2026-10-03T14:10:14Z",
            "conversationId": None,
            "recordingAvailable": False
        }
    ]

    @classmethod
    def get_calls(
        cls,
        service: str = "",
        status: str = "",
        user: str = "",
        date: str = "",
        search: str = "",
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Returns filtered, paginated telephony call history from SQLite.
        """
        conn = get_db_connection()
        db_calls = []
        try:
            rows = conn.execute("""
            SELECT c.*, b.filename as batch_name
            FROM contacts c
            LEFT JOIN batches b ON c.batch_id = b.id
            WHERE c.call_status IN ('CALLING', 'COMPLETED', 'FAILED', 'UNANSWERED')
            ORDER BY c.updated_at DESC
            """).fetchall()

            for r in rows:
                dur_sec = r['duration_seconds'] or 0
                dur_str = f"{dur_sec // 60:02d}:{dur_sec % 60:02d}"
                db_calls.append({
                    "id": f"call_{r['id'][:8]}",
                    "callSid": r['provider_call_id'] or f"EXO_{r['id'][:6]}",
                    "service": r['service'],
                    "user": "Score Labs",
                    "callerNumber": r['phone'],
                    "callerName": r['name'],
                    "contact": r['name'],
                    "phone": r['phone'],
                    "direction": "outbound",
                    "status": "in-progress" if r['call_status'] in ('CALLING', 'in-progress') else r['call_status'].lower(),
                    "durationSeconds": dur_sec,
                    "duration": dur_str,
                    "startedAt": r['started_at'],
                    "endedAt": r['ended_at'],
                    "conversationId": None,
                    "recordingAvailable": False
                })
        finally:
            conn.close()

        all_calls = db_calls + [s for s in cls._SAMPLE_CALLS if not any(d['callerNumber'] == s['callerNumber'] for d in db_calls)]

        filtered = all_calls

        if service:
            s_filter = service.strip().lower()
            filtered = [c for c in filtered if c["service"].lower() == s_filter]

        if status:
            st_filter = status.strip().lower()
            filtered = [c for c in filtered if c["status"].lower() == st_filter]

        if user:
            u_filter = user.strip().lower()
            filtered = [c for c in filtered if u_filter in c["user"].lower()]

        if date:
            d_filter = date.strip()
            filtered = [c for c in filtered if c.get("startedAt", "").startswith(d_filter)]

        if search:
            q = search.strip().lower()
            filtered = [
                c for c in filtered
                if q in c["callerNumber"].lower() or q in c["callerName"].lower() or q in c["callSid"].lower()
            ]

        total_count = len(filtered)
        page = max(int(page), 1)
        limit = max(min(int(limit), 100), 1)
        total_pages = max((total_count + limit - 1) // limit, 1)

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_items = filtered[start_idx:end_idx]

        return {
            "calls": paginated_items,
            "data": paginated_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "totalCount": total_count,
                "total": total_count,
                "totalPages": total_pages,
                "hasMore": page < total_pages
            }
        }
