# 10. REMO Comprehensive Error Handling & Voice Recovery Protocols

Voice channels are imperfect environments characterized by background noise, low-bandwidth codecs, line drops, and conversational collisions.

This document defines exact operational protocols for **17 distinct voice and technical failure scenarios**.

---

## The 17 Core Error Scenarios

---

### 1. Speech Recognition Failure (Empty / Low Confidence Transcript)
- **What happened**: STT engine returned empty text or a confidence score below acceptable threshold (<0.45).
- **What REMO should say**:
  - *Attempt 1*: *"I’m sorry, I didn’t quite catch that. Could you say that one more time?"*
  - *Attempt 2*: *"Sorry about that! My audio cut out for a second. Could you repeat that once more?"*
  - *Attempt 3*: *"I apologize, it seems we have a tricky audio connection. I don't want to keep making you repeat yourself—let me connect you with a team member or arrange a quick callback."*
- **What REMO should NOT say**: *"Speech recognition engine returned zero tokens"* or *"Your microphone is bad."*
- **Recovery action**: Reprompt politely. On 3rd failure, offer human transfer or callback.
- **Escalation condition**: 3 consecutive STT failures.

---

### 2. User Cannot Be Understood (Garbled / Incoherent Speech)
- **What happened**: Audio is received, but phonemes are unintelligible due to extreme background noise, heavy static, or severe mumbling.
- **What REMO should say**: *"I’m having a little trouble hearing you over the background noise. Would you mind repeating that just a bit slower?"*
- **What REMO should NOT say**: *"You are mumbling"* or *"Your voice is distorted."*
- **Recovery action**: Ask the user to slow down or spell key words.
- **Escalation condition**: Inaudibility persists across 3 turns.

---

### 3. Missing Information (Incomplete Slot)
- **What happened**: Caller omitted a required attribute (e.g., gave first name but no last name; gave date but no time).
- **What REMO should say**: *"Thanks, Marcus. And could I also get your last name to complete the profile?"*
- **What REMO should NOT say**: *"Input validation failed: last_name is null."*
- **Recovery action**: Isolate the single missing slot and ask specifically for it.
- **Escalation condition**: Caller repeatedly refuses to provide mandatory operational details.

---

### 4. Invalid Information (Format Failure)
- **What happened**: Caller provided an impossible value (e.g., 7-digit phone number, email without domain, Feb 31st).
- **What REMO should say**: *"It looks like that phone number was just a digit short. Could you repeat all ten digits for me?"*
- **What REMO should NOT say**: *"Regex pattern validation failed on input string."*
- **Recovery action**: Explain the specific discrepancy warmly and invite the caller to restate it.
- **Escalation condition**: 3 failed formatting attempts.

---

### 5. Tool Failure (Execution Error / Timeout)
- **What happened**: An internal tool call (e.g., calendar booking or candidate lookup) timed out or returned HTTP 500.
- **What REMO should say**: *"I’m experiencing a brief delay pulling up those records right now. Let me make a quick note of this so our team can finalize it and confirm back with you."*
- **What REMO should NOT say**: *"Internal server error 500 occurred in calendar API."*
- **Recovery action**: Cache conversation state locally in memory; queue offline retry.
- **Escalation condition**: Immediate escalation if caller requires real-time transaction confirmation.

---

### 6. Knowledge-Base Failure (Offline / Unresponsive Vector Index)
- **What happened**: Knowledge base query timed out or cluster unreachable.
- **What REMO should say**: *"I don't have that specific document available right now, and I want to make sure you get the accurate answer. Let me take down your question so our specialist can follow up."*
- **What REMO should NOT say**: *"Vector search connection pool exhausted."*
- **Recovery action**: Gracefully execute the Unknown Information Protocol (Doc 11).
- **Escalation condition**: Multiple caller questions fail lookup consecutively.

---

### 7. External API Failure (Third-Party CRM / ATS Timeout)
- **What happened**: Downstream system (Salesforce, HubSpot, Greenhouse) returned an API error.
- **What REMO should say**: *"I've noted down all your information here. Our backend system is doing a brief sync, so our team will review this and send your confirmation email within an hour."*
- **What REMO should NOT say**: *"Third-party CRM webhook timed out after 5000ms."*
- **Recovery action**: Fallback to local structured memory and future email notification queue.
- **Escalation condition**: None required if user was reassured without disruption.

---

### 8. Email Delivery Failure
- **What happened**: Notification dispatch worker failed to send confirmation or summary email.
- **What REMO should say**: *"I've saved everything on my end. In case there's any delay with email delivery, I've logged your confirmation code directly as #8902."*
- **What REMO should NOT say**: *"SMTP server rejected envelope recipient."*
- **Recovery action**: Provide verbal confirmation code; log error in background retry dead-letter queue.
- **Escalation condition**: None needed on voice call.

---

### 9. Database Failure (Write / Read Exception)
- **What happened**: Future persistence store crashed or failed connection handshake.
- **What REMO should say**: *"I've documented your request in our active queue. Our team is going to review your file directly and reach out to you."*
- **What REMO should NOT say**: *"Database write failed. Transaction rolled back."*
- **Recovery action**: Buffer caller payload in local memory cache or ephemeral disk buffer.
- **Escalation condition**: Offer human transfer if the caller is waiting for urgent validation.

---

### 10. Human Transfer Failure (All Lines Busy / PBX Drop)
- **What happened**: Live human queue has no available agents or PBX transfer fails.
- **What REMO should say**: *"I apologize, it looks like all of our team specialists are currently on other calls. Rather than keep you waiting on hold, can I take the best number to reach you so someone can call you right back?"*
- **What REMO should NOT say**: *"Transfer failed: SIP 486 Busy Here."*
- **Recovery action**: Capture caller's callback time window and phone number; flag as `CALLBACK_REQUIRED`.
- **Escalation condition**: Immediate priority callback ticket created.

---

### 11. User Gives Contradictory Information
- **What happened**: Caller provides conflicting statements (e.g., *"I have 2 years of experience"* then later *"I've been in this role since 2018"*).
- **What REMO should say**: *"Just so I make sure our hiring manager has your exact timeline, should I list your total experience as 2 years or since 2018?"*
- **What REMO should NOT say**: *"You just lied"* or *"You contradicted yourself earlier."*
- **Recovery action**: Gently present both statements side-by-side and ask the caller which one to record.
- **Escalation condition**: None; caller resolves discrepancy.

---

### 12. User Changes Information Mid-Call
- **What happened**: Caller says: *"Actually, don't use that email, use my work email instead."*
- **What REMO should say**: *"No problem at all! Let's update that to your work email. What address should I put down?"*
- **What REMO should NOT say**: *"We already submitted the previous email."*
- **Recovery action**: Overwrite previous entity value; confirm new entity aloud.
- **Escalation condition**: None.

---

### 13. User Asks Multiple Questions Simultaneously
- **What happened**: Caller rapid-fires: *"How much does it cost, how long does setup take, and do you support Salesforce?"*
- **What REMO should say**: *"I'd be happy to answer all three! First, setup typically takes less than 24 hours. Second, our standard plan starts at $499 a month. And third, yes, we fully integrate with Salesforce! Which of those would you like to explore deeper?"*
- **What REMO should NOT say**: *"Please ask only one question at a time."*
- **Recovery action**: Parse all questions, address each in 1 short sentence, then hand control back to the caller.
- **Escalation condition**: None.

---

### 14. User Becomes Frustrated or Agitated
- **What happened**: Caller raises voice, expresses anger: *"This is ridiculous, I've explained this three times!"*
- **What REMO should say**: *"I hear you, and I am truly sorry for the frustration. Let's get this sorted out right now. I can connect you directly with our senior supervisor who can take care of this immediately."*
- **What REMO should NOT say**: *"Please calm down"* or *"You are getting upset for no reason."*
- **Recovery action**: Empathize sincerely; bypass automated steps; initiate warm human transfer.
- **Escalation condition**: Immediate human transfer.

---

### 15. Caller Remains Silent (Dead Air)
- **What happened**: No audio detected for > 4 seconds.
- **What REMO should say**:
  - *At 4s*: *"Take your time, I'm right here whenever you're ready."*
  - *At 9s*: *"Hello? Are you still on the line?"*
  - *At 14s*: *"It sounds like we might have lost connection. I'll save our notes so far. Thanks for calling!"* (End call).
- **What REMO should NOT say**: Shouting or continuous repetitive prompts.
- **Recovery action**: Timed progressive prompts followed by polite disconnect.
- **Escalation condition**: None; disconnect after 15s total silence.

---

### 16. Caller Disconnects Unexpectedly
- **What happened**: Telephony carrier sends `HANGUP` event mid-conversation.
- **What REMO should say**: *[Session terminates on telephony layer]*
- **What REMO should NOT say**: N/A
- **Recovery action**: Save transcript and collected entities immediately. If call was mid-critical flow (e.g. ticket filing), mark status as `CALLBACK_REQUIRED` and queue notification.
- **Escalation condition**: Flag callback task for team.

---

### 17. Agent Loses Context / State Corruption
- **What happened**: In-memory dialogue state is desynchronized or LLM generates off-topic response.
- **What REMO should say**: *"Pardon me, I want to make sure I'm giving you the right assistance. Could you remind me what your main goal is today so I can take care of it?"*
- **What REMO should NOT say**: *"Context stack was purged"* or *"I forgot what we were talking about."*
- **Recovery action**: Reset dialogue state to intent identification without hanging up.
- **Escalation condition**: Transfer to human if caller shows irritation.

---

### 18. Excel Sheet Update Failure / File Lock (Future Implementation)
- **What happened**: Future Excel update tool encounters an OS file lock (e.g., workbook open in Excel by recruiter), corrupt file descriptor, or sheet permissions error.
- **What REMO should say**: *"I've noted down all your background details and preferences in our active recruitment queue. Our team is going to review your file directly and reach out to you."*
- **What REMO should NOT say**: *"PermissionError: [Errno 13] Permission denied candidate_tracker.xlsx"* or *"Workbook is currently locked for editing."*
- **Recovery action**: Immediately buffer the candidate row update payload to local encrypted memory and write to disk spool (`/spool/failed_excel_updates/{candidate_id}.json`). Background retry daemon attempts lock re-acquisition every 60 seconds.
- **Escalation condition**: Alert recruitment ops dashboard if file remains locked after 15 minutes.

---

### 19. Candidate Confirmation Email Dispatch Failure (Future Implementation)
- **What happened**: Future `sendCandidateConfirmationEmail` encounters an SMTP connection timeout, rate limit, or invalid mailbox rejection.
- **What REMO should say**: *"I have all your information safely recorded on our end. In case there's any brief delay with your confirmation email arriving, you can always reach our team directly at recruitment at [Company] dot com."*
- **What REMO should NOT say**: *"sendCandidateConfirmationEmail failed: SMTP 554 Transaction Failed."*
- **Recovery action**: Mark candidate Excel/DB field `confirmation_email_status` as `PENDING_RETRY`; queue email job in background exponential-backoff worker; do not fail the candidate screening outcome.
- **Escalation condition**: If rejection is permanent (e.g., mailbox does not exist), update status to `CALLBACK_REQUIRED` so recruiter can obtain valid email address.
