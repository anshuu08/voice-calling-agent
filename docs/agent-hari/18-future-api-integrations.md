# 18. REMO Future API Integrations & Ecosystem Architecture

> **NOTICE: ALL INTEGRATIONS LISTED HERE ARE FUTURE SPECIFICATIONS.**  
> No active accounts, SIP trunks, production credentials, or live vendor endpoints are configured in this repository. This document defines the interface boundaries, protocols, and data payloads that will be connected during Phase 3–8 of the implementation roadmap.

---

## 1. System Integration Matrix

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        REMO CONVERSATIONAL CORE                        │
└─────┬──────────────┬──────────────┬──────────────┬──────────────┬──────┘
      │              │              │              │              │
      ▼              ▼              ▼              ▼              ▼
 [Telephony]       [STT]          [LLM]          [TTS]       [Backend / DB]
 (Exotel/Twilio) (Deepgram/      (Gemini/     (ElevenLabs/   (Python/Node +
                 Whisper)       Claude/GPT)     Cartesia)     PostgreSQL)
```

---

## 2. Component Specifications

### A. Telephony Gateway (Future Candidates: Twilio, Exotel, LiveKit)
- **Role**: Ingest PSTN/SIP telephone calls, establish real-time two-way audio media streams, and manage PBX call control (hangup, dial, transfer).
- **Communication Protocol**: Secure WebSockets (`wss://`) with μ-law / PCM 8kHz or 16kHz audio frames.
- **Data Exchanged**:
  - *Inbound*: `CallSid`, `From` (Caller ID), `To` (Dialed Number), `CallStatus`, continuous inbound raw audio packets.
  - *Outbound*: Continuous synthesized speech audio packets, call control directives (`<Transfer>`, `<Hangup>`).

---

### B. Speech-to-Text (STT) Engine (Future Candidates: Deepgram Nova-2, OpenAI Whisper, AssemblyAI)
- **Role**: Convert streaming audio into low-latency punctuated text transcripts with word-level timestamps and endpointing.
- **Communication Protocol**: Streaming bidirectional WebSocket.
- **Data Exchanged**:
  - *Input*: 16kHz PCM audio buffers streamed every 20–50ms.
  - *Output*: Intermediate tokens, final transcript strings, confidence scores, end-of-speech markers (Voice Activity Detection).

---

### C. Large Language Model (LLM) Inference (Future Candidates: Google Gemini, Anthropic Claude, OpenAI GPT-4o)
- **Role**: Dialogue reasoning, intent classification, memory management, tool execution decision-making, and natural response synthesis.
- **Communication Protocol**: Streaming Server-Sent Events (SSE) or REST over HTTPS.
- **Data Exchanged**:
  - *Input*: System prompt, conversation history array, active mode context, tool definitions.
  - *Output*: Streaming generated conversational text tokens, structured tool calling JSON payloads (`tool_calls`).

---

### D. Voice / Text-to-Speech (TTS) Engine (Future Candidates: ElevenLabs Turbo v2.5, Cartesia Sonic, PlayHT)
- **Role**: Convert generated text into warm, expressive, ultra-low-latency voice audio matching REMO's persona.
- **Communication Protocol**: Streaming WebSocket / HTTP chunked transfer.
- **Data Exchanged**:
  - *Input*: Text token stream piped directly from LLM generation.
  - *Output*: 24kHz MP3 or 16kHz raw PCM audio frames streamed to telephony bridge.

---

### E. Backend Server & Dialogue Orchestrator (Future Candidates: Python/Flask/FastAPI or Node.js/Express)
- **Role**: Coordinate session lifecycles, manage in-memory state machines, enforce guardrails, and execute business logic tools.
- **Data Exchanged**: Coordinates payloads between telephony, STT, LLM, TTS, and databases.

---

### F. Relational Persistence Store (Future Candidates: PostgreSQL, MySQL)
- **Role**: Store immutable call audit records, structured candidate profiles, sales leads, support tickets, and performance metrics.
- **Data Exchanged**: Structured SQL CRUD operations with ACID guarantees.

---

### G. Transactional Email Provider (Future Candidates: SendGrid, Postmark, AWS SES, Resend)
- **Role**: Deliver instant lead alerts, candidate summaries, and ticket confirmations to human stakeholders.
- **Data Exchanged**: SMTP / REST payloads containing rendered HTML/text templates, metadata, and recipient emails.

---

### H. Enterprise CRM / ATS Systems (Future Candidates: Salesforce, HubSpot, Greenhouse, Lever)
- **Role**: Ingest qualified leads and candidates into corporate workflows.
- **Data Exchanged**: REST webhooks creating or updating Contacts, Deals, and Job Applications.

---

### I. Spreadsheet & Excel Integration Engine (Future Candidates: openpyxl, pandas, Microsoft Graph API, Google Sheets API)
- **Role**: Ingest candidate batches from `.xlsx` / `.csv` spreadsheets, match caller identity to candidate rows, update screening metrics, append recruiter notes, and update statuses without corrupting formulas, formatting, or column layouts.
- **Communication Protocol**: Local file I/O with concurrency locking (`portalocker` / `fasteners`) or OAuth2 REST over HTTPS.
- **Data Exchanged**:
  - *Input*: Candidate lookup keys (`phone_number`, `email`, `candidate_name`), verified attribute deltas.
  - *Output*: Updated spreadsheet cells, row index validation, commit status confirmation.

---

### J. Candidate Direct Confirmation Email Gateway (Future Candidates: SendGrid, Postmark, AWS SES, Resend)
- **Role**: Dispatch personalized post-call review emails directly to candidate inboxes containing all collected data, complete with a reply-to correction channel.
- **Communication Protocol**: REST HTTPS / SMTP with TLS.
- **Data Exchanged**:
  - *Input*: Verified candidate email address, screening metrics payload (name, phone, role, experience, location, notice period, salary).
  - *Output*: Unique message ID, delivery status receipt, bounce/reject telemetry.

---

## 3. Latency Budget Target (Future End-to-End Voice Loop)

To maintain a fluid, human-like cadence, the future voice loop must target a round-trip latency of **under 800 milliseconds**:

```text
[Caller Stops Speaking] ────► [Voice Activity Detection: 150ms]
                        ────► [STT Final Transcription: 150ms]
                        ────► [LLM Time to First Token: 250ms]
                        ────► [TTS Audio First Chunk:  150ms]
                        ────► [Telephony Buffer Out:    50ms]
─────────────────────────────────────────────────────────────
TOTAL LATENCY TARGET:         ~ 750 milliseconds (Human Cadence)
```
