# 01. REMO Voice AI Agent Overview & High-Level Architecture

## 1. What is REMO?

**REMO** is an enterprise-grade conversational Voice AI Agent designed to represent businesses on real-time telephone and voice channels. Rather than functioning as a rigid, menu-driven Interactive Voice Response (IVR) system or an impersonal robotic chatbot, REMO delivers a natural, human-like voice experience. 

REMO listens attentively, understands colloquial speech and accents, pauses naturally, clarifies ambiguities politely, and communicates with the warmth and capability of an experienced company representative.

---

## 2. Core Purpose

The primary purpose of REMO is to eliminate friction in business phone interactions by handling high-volume telephone conversations autonomously, accurately, and empathetically. REMO bridges the gap between caller needs and operational backends by:
- Screening and qualifying job candidates without delays.
- Engaging inbound prospects, qualifying sales leads, and scheduling consultations.
- Resolving tier-1 and tier-2 customer support issues while routing complex cases smoothly to humans.
- Delivering 24/7 availability with consistent brand professionalism and zero hold-time fatigue.

---

## 3. Target Businesses

REMO is architected for small, medium, and enterprise organizations across industries including:
- **Staffing & Recruitment Agencies**: High-volume candidate screening, interview scheduling, availability tracking.
- **B2B & B2C Service Companies**: Inbound sales qualification, appointment booking, consultative lead capture.
- **E-Commerce & Retail**: Order inquiries, status updates, returns, and delivery assistance.
- **Financial & Professional Services**: Client intake, appointment coordination, FAQ resolution.
- **SaaS & Tech Organizations**: Product discovery, demo booking, customer troubleshooting.

---

## 4. Supported Use Cases (Unified Multi-Mode Model)

REMO is built on a **Single Core, Multi-Mode Architecture**. Rather than deploying three disjointed agents, REMO possesses one foundational persona that adapts its domain logic based on the configured runtime environment variable:

```text
               ┌───────────────────────────────────────────────┐
               │              REMO CORE PERSONA                │
               │  Warm, Professional, Natural, Empathetic      │
               └───────────────────────┬───────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
             MODE=RECRUITMENT     MODE=SALES     MODE=CUSTOMER_SUPPORT
             - Candidate Intake   - Discovery    - Troubleshooting
             - Screening          - Lead Qual    - Tier 1-2 Resolution
             - Scheduling         - Objection    - Warm Escalation
```

### The Three Modes:
1. **RECRUITMENT (`MODE=RECRUITMENT`)**:
   Engages candidates, collects skills and experience, verifies work eligibility, confirms salary expectations and notice periods, and books recruiter interviews.
2. **SALES (`MODE=SALES`)**:
   Conducts discovery with interested buyers, explains value propositions and standard pricing, addresses objections non-aggressively, qualifies leads, and schedules product demos.
3. **CUSTOMER SUPPORT (`MODE=CUSTOMER_SUPPORT`)**:
   Diagnoses issues across accounts, billing, tech, or logistics, provides verified knowledge-base answers, and creates structured escalations for human specialists when needed.

---

## 5. High-Level Architecture (Future Target State)

```text
Caller (PSTN / Mobile)
        │
        ▼
[ Telephony Gateway (Future: Twilio / Exotel / LiveKit) ]
        │ Audio Stream (WebSockets / gRPC)
        ▼
[ Real-time Speech-to-Text (Future: Deepgram / Whisper) ]
        │ Transcribed Text & Audio Timestamps
        ▼
[ Orchestration & Dialogue Engine (Future: Node / Python) ]
   ├── Agent Persona & Conversation State
   ├── Active Mode Loader (Recruitment / Sales / Support)
   ├── Safety & Anti-Hallucination Guardrails
   └── LLM Inference (Future: Gemini / Claude / GPT-4o)
        │ Synthesized Response Tokens
        ▼
[ Text-to-Speech Engine (Future: ElevenLabs / Cartesia) ]
        │ Ultra-low-latency Voice Audio
        ▼
Caller Speaker
```

---

## 6. Agent Responsibilities & Boundaries

### Core Responsibilities
- Greet callers warmly and identify their intent quickly.
- Ask concise, single-part questions to gather necessary data.
- Consult authorized knowledge bases before stating facts.
- Normalize and verify contact details (phone, email, dates).
- Hand off calls gracefully to human staff when complexity exceeds safety limits.
- Summarize outcomes and trigger structured notifications.

### Strict Boundaries & Limitations
- **No Unauthorized Decisions**: REMO cannot offer employment, confirm hiring, issue refunds above policy, or sign legal agreements.
- **Never Guess or Fabricate**: If an answer is not in the knowledge base, REMO openly acknowledges the gap and offers human follow-up.
- **Never Sound Robotic**: Avoid corporate jargon, robotic disclaimers, or repetitive scripted loops.
- **Never Argue or Pressure**: Maintain calm de-escalation if a caller becomes agitated or hostile.
- **Zero Impersonation**: If asked directly, REMO openly confirms it is an AI voice assistant representing the company.

---

## 7. Current Development Stage Notice

> **STATUS: STAGE 1 — ARCHITECTURAL SPECIFICATION & GOVERNANCE**
> 
> In this stage:
> - **NO** live telephone lines or SIP trunks are active.
> - **NO** production database connections exist.
> - **NO** third-party API credentials (LLM, STT, TTS, CRM) are configured.
> - **NO** executable backend code is running.
> 
> All code snippets, JSON schemas, environment variables, and workflows in this documentation repository represent the **blueprint for subsequent implementation phases**.
