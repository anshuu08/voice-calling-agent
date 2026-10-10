# 16. REMO Email Notification Specification (Future Implementation)

> **STAGE 1 ARCHITECTURE DIRECTIVE**:  
> In early operating stages prior to full CRM or ATS database wiring, REMO delivers completed call outcomes directly to human administrators via structured email notifications.  
> **NO SMTP SERVERS, GMAIL APIS, OR SENDGRID INTEGRATIONS ARE IMPLEMENTED AT THIS STAGE.** This document defines the payload schemas, trigger rules, and environment configuration for future implementation.

---

## 1. Environment Variable Configuration

To ensure zero hard-coded personal email addresses, the destination recipient is controlled via environment variables:

```bash
# Future Email Configuration (.env)
REMO_NOTIFICATION_EMAIL=notifications@yourbusiness.com
# Backward-compatible alias:
AGENT_HARI_NOTIFICATION_EMAIL=notifications@yourbusiness.com
```

---

## 2. Notification Dispatch Triggers

An automated notification email is triggered immediately upon:
1. Completion of an inbound or outbound call where structured data was collected.
2. An mid-call escalation event where human follow-up or callback is required.
3. An emergency escalation where a live transfer failed due to busy lines.

---

## 3. Email Formats by Operational Mode

### Template 1: Recruitment Candidate Notification

```text
Subject: [REMO Alert] New Candidate Screened: {candidate_name} - {job_role}

--------------------------------------------------------------------------------
REMO VOICE AGENT - CANDIDATE SCREENING REPORT
--------------------------------------------------------------------------------
Call ID:          {call_sid}
Call Timestamp:   {call_timestamp}
Call Duration:    {call_duration} seconds
Status Assigned:  {candidate_status}

CANDIDATE DETAILS:
- Full Name:        {candidate_name}
- Phone Number:     {phone_number}
- Email Address:    {email}
- Current Location: {location}
- Target Job Role:  {job_role}

PROFESSIONAL BACKGROUND:
- Total Experience: {experience_years}
- Core Skills:      {skills_comma_separated}
- Current Role:     {current_role} at {current_company}
- Notice Period:    {notice_period}
- Salary Target:    {expected_salary}

CONVERSATION SUMMARY:
{conversation_summary}

RECRUITER ACTION REQUIRED:
{recruiter_notes_and_next_step}

FULL AUDIO / TRANSCRIPT RECORD:
[Link to secure transcript archive]
--------------------------------------------------------------------------------
```

---

### Template 2: Sales Lead Notification

```text
Subject: [REMO Lead] {interest_level} Intent: {lead_name} ({company_name})

--------------------------------------------------------------------------------
REMO VOICE AGENT - QUALIFIED INBOUND SALES LEAD
--------------------------------------------------------------------------------
Call ID:          {call_sid}
Call Timestamp:   {call_timestamp}
Lead Status:      {lead_status}
Interest Level:   {interest_level}

PROSPECT INFORMATION:
- Contact Name:   {lead_name}
- Phone Number:   {phone}
- Email:          {email}
- Company:        {company_name}

DISCOVERY & QUALIFICATION:
- Core Problem:   {requirement}
- Stated Budget:  {budget_range}
- Timeline:       {timeline}
- Preferred Plan: {product_tier}

SCHEDULED NEXT STEPS:
- Demo Booked:    {demo_date_time_or_none}
- Assigned AE:    {assigned_rep_or_round_robin}

CALL SUMMARY:
{conversation_summary}

SALES ACTION REQUIRED:
{action_items_and_notes}
--------------------------------------------------------------------------------
```

---

### Template 3: Customer Support Ticket Notification

```text
Subject: [REMO Support] Priority {priority}: Ticket #{ticket_id} ({category})

--------------------------------------------------------------------------------
REMO VOICE AGENT - SUPPORT CASE LOG
--------------------------------------------------------------------------------
Ticket Number:    {ticket_id}
Priority Level:   {priority}
Category:         {category}
Call Timestamp:   {call_timestamp}
Resolution:       {resolution_status}

CUSTOMER INFORMATION:
- Name:           {customer_name}
- Phone:          {phone}
- Email:          {email}
- Account ID:     {account_id}

ISSUE DESCRIPTION:
{issue_summary}

TROUBLESHOOTING ACTIONS TAKEN:
{troubleshooting_steps_completed}

ESCALATION & FOLLOW-UP:
- Reason:         {escalation_reason_or_none}
- Target Team:    {target_support_queue}
- Callback Time:  {preferred_callback_time_if_applicable}

AGENT TRANSCRIPT EXCERPT:
{critical_transcript_excerpt}
--------------------------------------------------------------------------------
```

---

### Template 4: Candidate Confirmation Email (Direct Outbound to Candidate)

> **PURPOSE**: Dispatched directly to the candidate's verified personal email address immediately following a recruitment call to verify accuracy and provide a correction mechanism.

```text
Subject: Please Confirm Your Information – [Company Name]

Hi [Candidate Name],

Thank you for speaking with REMO.

Please review the information we collected:

Name: [Name]
Phone: [Phone]
Email: [Email]
Role: [Role]
Experience: [Experience]
Location: [Location]
Notice Period: [Notice Period]
Expected Salary: [Salary]

Please reply to this email if any information is incorrect.

Thank you,
[Company Name]
Recruitment Team
```

#### Core Operational Rules for Candidate Confirmation Emails:
1. **Target Recipient Verification**: Send **only** to the specific email address provided and confirmed by the candidate during the call.
2. **Strict Single-Candidate Scope**: Include **only** information collected from that specific candidate during their call session.
3. **Zero Cross-Exposure**: Never expose or merge another candidate's information, notes, or history.
4. **Correction Channel**: The candidate may simply reply to this email to correct any discrepancies, routing the reply to the recruitment coordinator.
5. **Dispatch Logging**: The system records whether the email was sent (`confirmation_email_sent: true/false`, timestamp) in the candidate's Excel row and database record.
6. **Graceful Error Handling**: If dispatch encounters an SMTP/API failure, REMO does not crash the call; instead, it logs the job in a local retry queue and provides verbal reassurance.

---

## 4. Information Security (What NOT to Include in Emails)

To comply with data privacy standards:
- ❌ **NEVER** include unmasked credit card fragments or bank details in email bodies.
- ❌ **NEVER** transmit caller passwords or temporary authentication pins.
- ❌ **NEVER** include raw system prompt text or internal API keys.

---

## 5. Email Dispatch Failure Handling

When the future email dispatch service encounters an error (e.g., SMTP connection refused):
1. **Local Disk Spooling**: The JSON notification payload is immediately written to an encrypted ephemeral buffer file on disk (`/spool/failed_emails/{call_sid}.json`).
2. **Exponential Backoff Worker**: A background daemon retries delivery at 1m, 5m, 15m, and 60m intervals.
3. **Dead-Letter Alarm**: If delivery fails after 4 attempts, an incident alert is pushed to the system telemetry console without crashing the voice call runtime.
