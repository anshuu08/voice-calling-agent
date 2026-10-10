# 19. REMO Future Logical Database Design & Entity Architecture

> **NOTICE: SPECIFICATION ONLY — NO MIGRATIONS OR ACTIVE SCHEMAS CREATED.**  
> This document specifies the future relational database schema designed to support multi-tenant voice operations across Recruitment, Sales, and Customer Support.

---

## 1. Entity Relationship Overview

```text
[organizations] 1 ───< [users]
       │ 1
       └───< [agents] 1 ───< [calls] 1 ─── 1 [call_transcripts]
                               │ 1        1 ───< [agent_actions]
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼ 1                   ▼ 1                   ▼ 1
    [candidates]             [leads]          [support_tickets]
         │ 1                   │ 1                   │ 1
         ▼ N                   ▼ N                   ▼ N
[candidate_status_history] [follow_ups]        [follow_ups]
```

---

## 2. Core Entity Definitions

### 1. `organizations`
- **Purpose**: Multi-tenant customer accounts (companies using REMO).
- **Key Fields**: `id` (UUID, PK), `name` (VARCHAR), `slug` (VARCHAR, UNIQUE), `billing_tier` (VARCHAR), `created_at` (TIMESTAMP).
- **Relationships**: Has many `users`, `agents`, `candidates`, `leads`, `support_tickets`.

### 2. `users`
- **Purpose**: Human staff members, recruiters, account executives, and admins.
- **Key Fields**: `id` (UUID, PK), `org_id` (UUID, FK), `email` (VARCHAR, UNIQUE), `full_name` (VARCHAR), `role` (ENUM: `ADMIN`, `RECRUITER`, `SALES_REP`, `SUPPORT_AGENT`).

### 3. `agents`
- **Purpose**: Configured instances of REMO with specific voice IDs, prompt overrides, and modes.
- **Key Fields**: `id` (UUID, PK), `org_id` (UUID, FK), `agent_name` (VARCHAR, default "REMO"), `mode` (ENUM: `RECRUITMENT`, `SALES`, `CUSTOMER_SUPPORT`), `phone_number` (VARCHAR, E.164), `voice_id` (VARCHAR), `status` (ENUM: `ACTIVE`, `PAUSED`).

### 4. `calls`
- **Purpose**: Immutable call log records for every telephony interaction.
- **Key Fields**: `id` (UUID, PK), `agent_id` (UUID, FK), `org_id` (UUID, FK), `call_sid` (VARCHAR, UNIQUE), `caller_number` (VARCHAR), `direction` (ENUM: `INBOUND`, `OUTBOUND`), `duration_seconds` (INT), `status` (ENUM: `COMPLETED`, `FAILED`, `BUSY`, `NO_ANSWER`), `started_at` (TIMESTAMP), `ended_at` (TIMESTAMP).

### 5. `call_transcripts`
- **Purpose**: Complete dialogue turn history and audio analysis metrics.
- **Key Fields**: `id` (UUID, PK), `call_id` (UUID, FK, UNIQUE), `raw_transcript` (JSONB / TEXT), `sentiment_score` (VARCHAR), `summary` (TEXT), `audio_recording_url` (VARCHAR, NULLABLE).

### 6. `candidates`
- **Purpose**: Structured applicant profiles captured during recruitment calls.
- **Key Fields**: `id` (UUID, PK), `org_id` (UUID, FK), `call_id` (UUID, FK), `candidate_name` (VARCHAR), `phone_number` (VARCHAR), `email` (VARCHAR), `job_role` (VARCHAR), `experience_years` (NUMERIC), `skills` (TEXT[]), `current_company` (VARCHAR), `current_role` (VARCHAR), `notice_period` (VARCHAR), `expected_salary` (VARCHAR), `status` (ENUM: `NEW`, `SCREENING`, `SHORTLISTED`, `INTERVIEW_SCHEDULED`, `ON_HOLD`, `REJECTED`, `SELECTED`, `COMPLETED`, `CALLBACK_REQUIRED`).

### 7. `candidate_status_history`
- **Purpose**: Audit log of recruitment lifecycle status changes.
- **Key Fields**: `id` (UUID, PK), `candidate_id` (UUID, FK), `from_status` (VARCHAR), `to_status` (VARCHAR), `changed_by` (VARCHAR), `notes` (TEXT), `timestamp` (TIMESTAMP).

### 8. `leads`
- **Purpose**: Inbound sales leads and commercial discovery prospects.
- **Key Fields**: `id` (UUID, PK), `org_id` (UUID, FK), `call_id` (UUID, FK), `lead_name` (VARCHAR), `phone` (VARCHAR), `email` (VARCHAR), `company_name` (VARCHAR), `requirement` (TEXT), `budget_range` (VARCHAR), `timeline` (VARCHAR), `interest_level` (ENUM: `HIGH`, `MEDIUM`, `LOW`), `status` (ENUM: `NEW`, `QUALIFIED`, `INTERESTED`, `FOLLOW_UP`, `DEMO_REQUESTED`, `HUMAN_REQUIRED`, `NOT_INTERESTED`, `CONVERTED`).

### 9. `customers`
- **Purpose**: Master directory of existing client accounts for support lookup.
- **Key Fields**: `id` (UUID, PK), `org_id` (UUID, FK), `account_number` (VARCHAR, UNIQUE), `customer_name` (VARCHAR), `primary_phone` (VARCHAR), `primary_email` (VARCHAR), `tier` (VARCHAR).

### 10. `support_tickets`
- **Purpose**: Customer support cases and technical incident logs.
- **Key Fields**: `id` (UUID, PK), `ticket_code` (VARCHAR, UNIQUE, e.g. "TICK-2026-8902"), `org_id` (UUID, FK), `call_id` (UUID, FK), `customer_id` (UUID, FK, NULLABLE), `category` (ENUM: `Account`, `Billing`, `Technical issue`, `Product issue`, `Service issue`, `Complaint`, `Refund`, `Cancellation`, `General information`), `priority` (ENUM: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), `issue_summary` (TEXT), `resolution_status` (ENUM: `OPEN`, `RESOLVED`, `ESCALATED_TO_HUMAN`, `CALLBACK_REQUIRED`), `created_at` (TIMESTAMP).

### 11. `follow_ups`
- **Purpose**: Scheduled appointments, recruiter interviews, and callback promises.
- **Key Fields**: `id` (UUID, PK), `org_id` (UUID, FK), `call_id` (UUID, FK), `scheduled_time` (TIMESTAMP), `type` (ENUM: `INTERVIEW`, `DEMO`, `CALLBACK`, `AGENT_FOLLOWUP`), `assigned_to` (UUID, FK `users`), `status` (ENUM: `SCHEDULED`, `COMPLETED`, `CANCELLED`, `MISSED`).

### 12. `knowledge_base`
- **Purpose**: Indexed documentation chunks for RAG lookups during live calls.
- **Key Fields**: `id` (UUID, PK), `org_id` (UUID, FK), `title` (VARCHAR), `category` (VARCHAR), `content` (TEXT), `embedding` (VECTOR, 1536/768 dim), `last_updated` (TIMESTAMP).

### 13. `agent_actions`
- **Purpose**: Audit log of all tool executions and function calls triggered by REMO.
- **Key Fields**: `id` (UUID, PK), `call_id` (UUID, FK), `tool_name` (VARCHAR), `input_payload` (JSONB), `output_payload` (JSONB), `execution_duration_ms` (INT), `success` (BOOLEAN), `timestamp` (TIMESTAMP).
