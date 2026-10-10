# 08. REMO Call Flow Specifications & State Transitions

This document maps out the state machine, decision trees, and interaction flows governing calls handled by REMO.

---

## 1. Master Call Flow Architecture (Generic Lifecycle)

```text
               [ CALL START: Inbound Ring / Outbound Connect ]
                                     │
                                     ▼
                            [ 1. Warm Greeting ]
                                     │
                                     ▼
                        [ 2. Identify Caller Intent ]
                                     │
                                     ▼
                        [ 3. Select Operating Mode ]
                                     │
                   ┌─────────────────┼─────────────────┐
                   ▼                 ▼                 ▼
             [RECRUITMENT]        [SALES]          [SUPPORT]
                   │                 │                 │
                   └─────────────────┼─────────────────┘
                                     │
                                     ▼
                        [ 4. Understand Request ]
                                     │
                                     ▼
                    [ 5. Ask Required Discovery Questions ]
                     (One single-part question per turn)
                                     │
                                     ▼
                     [ 6. Consult Knowledge Base / Tool ]
                                     │
                   ┌─────────────────┴─────────────────┐
                   │                                   │
              [Found / Valid]                   [Unknown / Disputed]
                   │                                   │
                   ▼                                   ▼
          [ 7. Deliver Response ]             [ 11-Unknown Protocol ]
                   │                         (Offer Human Follow-up)
                   ▼                                   │
       [ 8. Take Permitted Action ]                    │
         (Schedule / Log Lead / Ticket)                │
                   │                                   │
                   ▼                                   │
       [ 9. Confirm & Summarize Outcome ] <────────────┘
                   │
                   ▼
       [ 10. Check for Additional Needs ]
        ("Is there anything else I can help with?")
                   │
          ┌────────┴────────┐
        [Yes]              [No]
          │                 │
     (Loop to #4)           ▼
                   [ 11. Polite Closing & Disconnect ]
```

---

## 2. Recruitment Call Flow State Diagram

```text
[State: RC_GREETING]
  │
  ├──> [State: RC_CONFIRM_ROLE]
  │      └── "Are you interested in our Senior Backend opening?"
  │
  ├──> [State: RC_SCREEN_EXPERIENCE]
  │      └── "How many years of backend experience do you have?"
  │
  ├──> [State: RC_SCREEN_SKILLS]
  │      └── "What are your core programming languages?"
  │
  ├──> [State: RC_SCREEN_LOGISTICS]
  │      ├── Notice Period
  │      ├── Expected Compensation
  │      └── Location / Remote preference
  │
  ├──> [State: RC_DECISION_ROUTING]
  │      ├── Meets Baseline Criteria ──> [State: RC_SCHEDULE_INTERVIEW]
  │      └── Unclear / Divergent ───────> [State: RC_RECORD_FOR_RECRUITER]
  │
  └──> [State: RC_SUMMARY_CLOSE]
         └── Summarize next recruiter action -> Confirm email -> Friendly close.
```

---

## 3. Sales Call Flow State Diagram

```text
[State: SC_GREETING]
  │
  ├──> [State: SC_NEEDS_DISCOVERY]
  │      └── "What challenges are you hoping to solve with voice automation?"
  │
  ├──> [State: SC_VALUE_MAPPING]
  │      └── Explain verified capabilities matching caller's pain points.
  │
  ├──> [State: SC_PRICING_ALIGNMENT]
  │      └── Present standard tier pricing transparently.
  │
  ├──> [State: SC_OBJECTION_HANDLING]
  │      ├── Budget Concerns ──> Acknowledge ROI + Share case study.
  │      └── Competitor ───────> Highlight unique integration points.
  │
  ├──> [State: SC_QUALIFICATION_CHECK]
  │      ├── Decision timeline?
  │      └── Call volume requirements?
  │
  ├──> [State: SC_NEXT_ACTION]
  │      ├── High Intent ──────> [State: SC_BOOK_DEMO]
  │      ├── Needs Info ───────> [State: SC_EMAIL_COLLATERAL]
  │      └── Enterprise Scale ─> [State: SC_WARM_SALES_TRANSFER]
  │
  └──> [State: SC_SUMMARY_CLOSE]
         └── Confirm demo details -> Send calendar invite -> End politely.
```

---

## 4. Customer Support Call Flow State Diagram

```text
[State: CS_GREETING]
  │
  ├──> [State: CS_INTAKE_EMPATHY]
  │      └── Validate caller frustration; identify category (Billing/Tech/Account).
  │
  ├──> [State: CS_SEVERITY_TRIAGE]
  │      ├── CRITICAL (Outage/Security) ──> [State: CS_IMMEDIATE_TRANSFER]
  │      └── LOW - HIGH ───────────────────> [State: CS_ISOLATE_ISSUE]
  │
  ├──> [State: CS_TROUBLESHOOTING_STEP_1]
  │      └── Suggest verified primary fix from knowledge base.
  │      ├── Resolved? ───────────────────> [State: CS_CONFIRM_RESOLUTION]
  │      └── Not Resolved? ───────────────> [State: CS_TROUBLESHOOTING_STEP_2]
  │
  ├──> [State: CS_TROUBLESHOOTING_STEP_2]
  │      └── Suggest secondary verified remediation.
  │      ├── Resolved? ───────────────────> [State: CS_CONFIRM_RESOLUTION]
  │      └── Still Failed? ───────────────> [State: CS_LOG_TICKET_ESCALATE]
  │
  ├──> [State: CS_LOG_TICKET_ESCALATE]
  │      └── Generate ticket -> Dispatch priority notification -> Provide ticket ID.
  │
  └──> [State: CS_SUMMARY_CLOSE]
         └── Confirm next callback timeline -> Friendly close.
```

---

## 5. Global State Transition Guardrails

1. **Safety Interrupt**: At any point, if the caller requests a human or displays severe agitation, state transitions immediately jump to `GLOBAL_WARM_TRANSFER`.
2. **Loop Prevention**: If an agent remains in the same discovery or troubleshooting state for more than 2 turns due to unclear audio or unparseable input, REMO transitions to `RECOVERY_CLARIFICATION` or `ESCALATE_TO_OFFLINE_FOLLOWUP`.
3. **No Dead Ends**: Every conversational branch has a defined terminal state that ensures the caller receives a scheduled meeting, a logged ticket, a human transfer, or an explicit promise of follow-up.
