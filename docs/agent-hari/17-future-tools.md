# 17. REMO Future Tool & Function Calling Specifications

> **STATUS: FUTURE IMPLEMENTATION**  
> These tool definitions specify function calling interfaces that will be registered with the LLM in Phase 8 of implementation. **NO FUNCTION EXECUTORS OR API ENDPOINTS ARE IMPLEMENTED AT THIS STAGE.**

---

## Tool 1: `knowledgeBaseSearch`
- **Purpose**: Search the verified company knowledge base for answers to questions regarding policies, product specs, pricing, and FAQs.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Natural language search phrase" },
      "category": { "type": "string", "enum": ["recruitment", "sales", "support", "general"] }
    },
    "required": ["query"]
  }
  ```
- **Output Schema**:
  ```json
  { "results": [{ "snippet": "string", "source_document": "string", "confidence_score": 0.92 }] }
  ```
- **When to Use**: When a caller asks a factual question about services, pricing, company policies, or benefits.
- **When NOT to Use**: For standard conversational small talk or when data was already retrieved in the conversation context.
- **Error Behavior**: Returns empty array `[]`; triggers Unknown Information Protocol.

---

## Tool 2: `createCandidate`
- **Purpose**: Create a new candidate profile in the recruitment tracking system.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "candidate_name": { "type": "string" },
      "phone_number": { "type": "string" },
      "email": { "type": "string" },
      "job_role": { "type": "string" },
      "experience_years": { "type": "number" },
      "skills": { "type": "array", "items": { "type": "string" } },
      "notice_period": { "type": "string" },
      "expected_salary": { "type": "string" }
    },
    "required": ["candidate_name", "phone_number", "job_role"]
  }
  ```
- **Output Schema**:
  ```json
  { "candidate_id": "CAND-10492", "status": "SCREENING", "success": true }
  ```
- **When to Use**: At the end of an initial candidate screening intake once core parameters are verified.
- **When NOT to Use**: Before candidate confirms intent, or during non-recruitment calls.
- **Error Behavior**: Caches candidate object locally and queues email notification.

---

## Tool 3: `updateCandidate`
- **Purpose**: Update an existing candidate profile with additional notes, status, or rescheduled interview details.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "candidate_id": { "type": "string" },
      "candidate_status": { "type": "string" },
      "recruiter_notes": { "type": "string" }
    },
    "required": ["candidate_id"]
  }
  ```
- **Output Schema**: `{ "updated": true, "candidate_id": "CAND-10492" }`
- **When to Use**: When a candidate provides updated contact details or completes a follow-up interview.
- **When NOT to Use**: If `candidate_id` cannot be verified.
- **Error Behavior**: Logs error; informs caller notes have been recorded for manual sync.

---

## Tool 4: `createLead`
- **Purpose**: Register a qualified sales lead into the CRM.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "lead_name": { "type": "string" },
      "phone": { "type": "string" },
      "email": { "type": "string" },
      "company_name": { "type": "string" },
      "requirement": { "type": "string" },
      "budget_range": { "type": "string" },
      "timeline": { "type": "string" },
      "interest_level": { "type": "string", "enum": ["HIGH", "MEDIUM", "LOW"] }
    },
    "required": ["lead_name", "phone", "requirement"]
  }
  ```
- **Output Schema**: `{ "lead_id": "LEAD-77401", "success": true }`
- **When to Use**: Once a prospect shares requirements and agrees to follow-up or demo booking.
- **When NOT to Use**: During casual consumer FAQ calls without business intent.
- **Error Behavior**: Buffers payload; logs lead via fallback email.

---

## Tool 5: `updateLead`
- **Purpose**: Modify lead status or add notes from follow-up calls.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "lead_id": { "type": "string" },
      "lead_status": { "type": "string" },
      "notes": { "type": "string" }
    },
    "required": ["lead_id"]
  }
  ```
- **Output Schema**: `{ "updated": true, "lead_id": "LEAD-77401" }`
- **When to Use**: When an existing prospect requests a change in timeline or cancels a demo.
- **When NOT to Use**: If lead identity cannot be verified.
- **Error Behavior**: Logs update failure; notifies sales rep.

---

## Tool 6: `createSupportTicket`
- **Purpose**: Create a new customer support ticket with category and priority.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "customer_name": { "type": "string" },
      "phone": { "type": "string" },
      "email": { "type": "string" },
      "account_id": { "type": "string" },
      "category": { "type": "string" },
      "priority": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"] },
      "issue_summary": { "type": "string" }
    },
    "required": ["customer_name", "phone", "category", "issue_summary"]
  }
  ```
- **Output Schema**: `{ "ticket_id": "TICK-2026-8902", "status": "OPEN", "success": true }`
- **When to Use**: When a support issue cannot be resolved on the call or requires follow-up.
- **When NOT to Use**: If caller issue was solved in-call and confirmed by caller.
- **Error Behavior**: Generates fallback ticket ID locally and gives it to caller.

---

## Tool 7: `sendEmail`
- **Purpose**: Trigger an automated transactional email to caller or admin.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "recipient": { "type": "string" },
      "subject": { "type": "string" },
      "template_id": { "type": "string" },
      "template_data": { "type": "object" }
    },
    "required": ["recipient", "subject", "template_id"]
  }
  ```
- **Output Schema**: `{ "sent": true, "message_id": "msg_90128" }`
- **When to Use**: To dispatch calendar invites, application receipts, or lead alerts.
- **When NOT to Use**: With unverified email addresses.
- **Error Behavior**: Queues message in spool for background retry.

---

## Tool 8: `transferCall`
- **Purpose**: Signal the telephony platform to execute a SIP/PSTN blind or warm transfer.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "target_queue": { "type": "string" },
      "reason": { "type": "string" },
      "priority": { "type": "string" },
      "context_payload": { "type": "object" }
    },
    "required": ["target_queue", "reason"]
  }
  ```
- **Output Schema**: `{ "transfer_initiated": true, "dial_status": "CONNECTING" }`
- **When to Use**: When escalation conditions are met or caller explicitly asks for a human.
- **When NOT to Use**: Before caller has been politely informed of the transfer.
- **Error Behavior**: Executes Fallback Protocol (captures callback number).

---

## Tool 9: `scheduleInterview`
- **Purpose**: Book a candidate interview directly on the recruiter's calendar.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "candidate_id": { "type": "string" },
      "date_time_iso": { "type": "string" },
      "recruiter_id": { "type": "string" },
      "duration_minutes": { "type": "integer" }
    },
    "required": ["candidate_id", "date_time_iso"]
  }
  ```
- **Output Schema**: `{ "confirmed": true, "calendar_event_link": "https://..." }`
- **When to Use**: When a candidate selects an available time slot.
- **When NOT to Use**: If date/time has not been explicitly confirmed by the candidate.
- **Error Behavior**: Apologizes and offers alternative time slots.

---

## Tool 10: `scheduleCallback`
- **Purpose**: Reserve a future callback time window for a human rep or REMO.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "phone": { "type": "string" },
      "name": { "type": "string" },
      "preferred_time": { "type": "string" },
      "topic": { "type": "string" }
    },
    "required": ["phone", "preferred_time"]
  }
  ```
- **Output Schema**: `{ "callback_scheduled": true, "time_window": "string" }`
- **When to Use**: When transfer fails or caller is in a rush and requests a callback.
- **When NOT to Use**: When caller prefers immediate assistance.
- **Error Behavior**: Informs caller request is recorded in priority queue.

---

## Tool 11: `lookupCustomer`
- **Purpose**: Retrieve customer record by phone number or account ID.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "phone_number": { "type": "string" },
      "account_id": { "type": "string" }
    }
  }
  ```
- **Output Schema**: `{ "found": true, "customer": { "name": "string", "account_tier": "Enterprise" } }`
- **When to Use**: At the start of a customer support call to identify the caller.
- **When NOT to Use**: During cold recruitment screening calls.
- **Error Behavior**: Informs caller record wasn't found; prompts for name and email manually.

---

## Tool 12: `lookupCandidate`
- **Purpose**: Search for an existing candidate record by email or phone.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "email": { "type": "string" },
      "phone_number": { "type": "string" }
    }
  }
  ```
- **Output Schema**: `{ "found": true, "candidate_status": "SHORTLISTED", "job_role": "Backend Engineer" }`
- **When to Use**: When a caller inquires about their existing job application status.
- **When NOT to Use**: For brand new applicant screening.
- **Error Behavior**: States profile is not located; offers to initiate a new application.

---

## Tool 13: `lookupOrder`
- **Purpose**: Check the real-time shipping or fulfillment status of an order.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "order_number": { "type": "string" },
      "postal_code": { "type": "string" }
    },
    "required": ["order_number"]
  }
  ```
- **Output Schema**: `{ "order_id": "ORD-1294", "status": "IN_TRANSIT", "eta": "2026-10-07" }`
- **When to Use**: When a caller asks "Where is my order?"
- **When NOT to Use**: Without verifying the order number.
- **Error Behavior**: Informs caller order details are pending carrier sync; offers human escalation.

---

## Tool 14: `readCandidateExcel` (Excel Candidate Retrieval Tool)
- **Purpose**: Look up and read candidate details from an incoming recruitment Excel spreadsheet. Identify the candidate being called using phone number, email, or candidate name.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "phone_number": { "type": "string", "description": "Candidate phone number in E.164 or 10-digit format" },
      "email": { "type": "string", "description": "Candidate email address" },
      "candidate_name": { "type": "string", "description": "Full candidate name" }
    }
  }
  ```
- **Output Schema**:
  ```json
  {
    "found": true,
    "candidate": {
      "candidate_name": "Sarah Jenkins",
      "phone_number": "+14155550198",
      "email": "sarah.jenkins@example.com",
      "job_role": "Senior Backend Developer",
      "experience": "5 years",
      "skills": "Python, FastAPI, AWS",
      "location": "Austin, TX",
      "expected_salary": "$125,000 USD/year",
      "notice_period": "30 days",
      "status": "NEW",
      "notes": "Sourced via LinkedIn campaign"
    },
    "excel_row_index": 14
  }
  ```
- **When to Use**: Prior to or at the start of a recruitment screening call to load the candidate's existing context from the Excel sheet.
- **When NOT to Use**: During sales or customer support calls, or without an active candidate identifier.
- **Error Behavior**: Returns `found: false`; REMO gracefully prompts the candidate for basic introductory details without interruption.

---

## Tool 15: `updateCandidateExcel` (Excel Update Tool)
- **Purpose**: Update candidate details, call notes, and lifecycle status in the candidate Excel sheet after a screening call. Preserves sheet structure, formulas, and existing unedited columns; never overwrites with blanks.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "excel_row_index": { "type": "integer", "description": "Row index of candidate in spreadsheet" },
      "phone_number": { "type": "string" },
      "email": { "type": "string" },
      "candidate_name": { "type": "string" },
      "experience": { "type": "string" },
      "skills": { "type": "string" },
      "location": { "type": "string" },
      "expected_salary": { "type": "string" },
      "notice_period": { "type": "string" },
      "status": {
        "type": "string",
        "enum": [
          "NEW",
          "CONTACTED",
          "INTERESTED",
          "NOT_INTERESTED",
          "SHORTLISTED",
          "ON_HOLD",
          "REJECTED",
          "CALLBACK_REQUIRED",
          "COMPLETED"
        ]
      },
      "notes": { "type": "string", "description": "Screening summary and interview observations" }
    },
    "required": ["status"]
  }
  ```
- **Output Schema**:
  ```json
  {
    "success": true,
    "updated_row": 14,
    "status": "SHORTLISTED",
    "updated_fields": ["experience", "expected_salary", "notice_period", "status", "notes"],
    "timestamp": "2026-10-05T10:58:30Z"
  }
  ```
- **When to Use**: At the conclusion of a recruitment screening call after the candidate has verbally confirmed their updated information.
- **When NOT to Use**: When information has not been verified by the candidate, or to delete rows/columns.
- **Error Behavior**: Caches payload in local disk retry buffer (`/spool/failed_excel_updates/`); does not interrupt call.

---

## Tool 16: `sendCandidateConfirmationEmail`
- **Purpose**: Send a structured review and confirmation email directly to the candidate's provided email address so they can review collected metrics and reply with corrections.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "candidate_name": { "type": "string" },
      "candidate_email": { "type": "string" },
      "phone": { "type": "string" },
      "job_role": { "type": "string" },
      "experience": { "type": "string" },
      "location": { "type": "string" },
      "notice_period": { "type": "string" },
      "expected_salary": { "type": "string" },
      "company_name": { "type": "string" }
    },
    "required": ["candidate_name", "candidate_email", "job_role"]
  }
  ```
- **Output Schema**:
  ```json
  {
    "success": true,
    "message_id": "c_conf_msg_77210",
    "recipient": "sarah.jenkins@example.com",
    "dispatched_at": "2026-10-05T10:58:30Z"
  }
  ```
- **When to Use**: At the end of a candidate screening call where candidate details were gathered or modified.
- **When NOT to Use**: If candidate email was not verified, or with another candidate's email.
- **Error Behavior**: Marks candidate record `confirmation_email_status: "FAILED_RETRY"`; logs job in exponential backoff spooler.
