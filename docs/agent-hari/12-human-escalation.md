# 12. REMO Human Escalation & Handoff Protocols

Automated voice agents exist to assist, not trap, human callers. REMO is engineered to facilitate warm, contextual transitions to human personnel whenever automated handling is insufficient, undesirable to the caller, or unsafe.

---

## 1. Mandatory Escalation Triggers

REMO must immediately initiate escalation under any of the following 12 conditions:

1. **Explicit Caller Request**: The caller states: *"Let me speak to a person,"* *"I want an agent,"* *"Get me someone real,"* or *"Give me a manager."*
2. **Acute Caller Frustration or Hostility**: Caller is shouting, using abusive language, or expressing high distress.
3. **Sensitive Complaints**: Accusations of discrimination, severe misconduct, or gross service failure.
4. **Legal Claims or Regulatory Inquiries**: Mentions of lawsuits, attorneys, subpoenas, or regulatory complaints (FTC, CFPB, etc.).
5. **Payment & Billing Disputes**: Unresolved double-billing or charges over authorized policy thresholds.
6. **Disputed Refunds**: Demands for non-standard refunds or compensation.
7. **High-Value Enterprise Opportunities**: Large corporate buyers or enterprise contracts requiring custom pricing and executive discovery.
8. **Recruitment Exceptions**: Senior executive candidates, salary negotiations, or candidate requests for detailed feedback.
9. **Persistent Knowledge Deficit**: Two consecutive questions cannot be answered by the knowledge base.
10. **Repeated Tool or System Failures**: System encounters 2 consecutive backend timeouts or errors.
11. **Persistent Speech Recognition Inaudibility**: Caller cannot be understood after 3 consecutive attempts.
12. **Account Security & Fraud Concerns**: Compromised accounts, identity theft, unauthorized access reports.

---

## 2. The 3-Step Warm Escalation Protocol

When initiating a transfer, REMO follows a transparent 3-step sequence:

```text
[ 1. Explain the Action Warmly ]
"I would be glad to connect you directly with a specialist from our team."
                 │
                 ▼
[ 2. Confirm and Reassure Context Continuity ]
"I've noted down all the details we just covered so you won't have to repeat yourself."
                 │
                 ▼
[ 3. Execute PBX / Telephony SIP Transfer ]
"Please hold for just a few seconds while I get them on the line."
```

### Complete Voice Script
> *"I completely understand, and I'd be glad to connect you with one of our senior specialists who can take care of this for you right away. I've already documented everything we talked about so you won't have to repeat yourself. One moment while I transfer you over."*

---

## 3. Fallback Protocol When Transfer Fails (Lines Busy / After Hours)

If the telephony system returns a busy signal, timeout, or off-hours status:

> *"I apologize, it looks like our specialists are temporarily tied up assisting other callers right now. Rather than leaving you on hold, can I take down your name and phone number so our team can call you directly within the next 30 minutes?"*

### Fallback Information Capture:
1. Confirm callback number.
2. Confirm best time window (e.g., *"morning"* or *"within the next hour"*).
3. Log record as priority `CALLBACK_REQUIRED`.

---

## 4. Context Handover Payload Schema (Future Telephony / CRM Sync)

When REMO initiates a transfer, a structured metadata packet is sent to the human agent's desktop screen pop:

```json
{
  "call_sid": "CA_9948201a883e",
  "caller_number": "+14155550183",
  "customer_name": "Marcus Vance",
  "operating_mode": "CUSTOMER_SUPPORT",
  "escalation_reason": "BILLING_DISPUTE_DUPLICATE_CHARGE",
  "priority": "HIGH",
  "key_entities_collected": {
    "account_id": "ACC-44910",
    "transaction_date": "2026-10-01",
    "disputed_amount": "$499.00",
    "verified_email": "marcus.v@cloudcorp.io"
  },
  "dialogue_turns_count": 6,
  "conversation_summary": "Customer called reporting two $499 charges on their credit card for the annual plan renewal. Verified that duplicate transaction occurred due to gateway retry. Customer requested immediate refund.",
  "sentiment_score": "FRUSTRATED_CALMED",
  "transfer_target_queue": "tier_2_billing_finance"
}
```

This ensures the receiving human representative has complete context before answering the line.
