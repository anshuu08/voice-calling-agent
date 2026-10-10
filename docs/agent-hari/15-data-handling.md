# 15. REMO Data Handling, Entity Schemas & Retention Governance

> **NOTICE**: This document specifies data definitions, validation rules, and future database mappings for planning purposes. **NO ACTIVE DATABASE IS CONFIGURED OR CONNECTED AT THIS STAGE.**

---

## 1. Domain Data Models

### A. Common Data (All Calls)
Captured during every call regardless of operational mode.

| Field Name | Type | Requirement | Sensitivity | Validation Rule | Spoken Confirmation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `call_sid` | String | System Generated | Low | Non-empty unique string | No |
| `caller_phone` | String | Required | Medium | E.164 or 10-digit regex | Yes (repeat back) |
| `caller_name` | String | Required | Low | Min 2 characters, alpha | Yes |
| `call_timestamp`| ISO 8601 | System Generated | Low | UTC timestamp | No |
| `operating_mode`| Enum | Required | Low | `RECRUITMENT` \| `SALES` \| `CUSTOMER_SUPPORT` | Implicit |
| `transcript` | String | System Generated | Medium | Full text array | No |
| `sentiment` | Enum | System Generated | Low | `POSITIVE` \| `NEUTRAL` \| `FRUSTRATED` | No |
| `call_duration` | Integer | System Generated | Low | Non-negative integer (seconds)| No |

---

### B. Recruitment Data Model (`MODE=RECRUITMENT`)

| Field Name | Type | Requirement | Sensitivity | Validation Rule | Spoken Confirmation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `candidate_name` | String | Required | Low | Full name | Yes |
| `phone_number` | String | Required | Medium | Validated phone number | Yes |
| `email` | String | Required | Medium | Valid email format (`@`, `.`) | Yes (spell domain) |
| `location` | String | Required | Low | City, State or Country | Yes |
| `job_role` | String | Required | Low | Target open job title | Yes |
| `experience_years`| Float | Required | Low | 0.0 - 50.0 years | Yes |
| `skills` | Array[String]| Required | Low | List of parsed skills | Summary confirmation |
| `current_company` | String | Optional | Low | Company name | Optional |
| `current_role` | String | Optional | Low | Job title | Optional |
| `notice_period` | String | Required | Low | Duration (e.g. Immediate, 30 days) | Yes |
| `expected_salary`| String | Optional | High | Currency / amount range | Yes |
| `candidate_status`| Enum | Required | Low | `NEW`, `SCREENING`, `SHORTLISTED`, etc. | Implicit |
| `recruiter_notes` | String | System Generated | Low | Qualitative text summary | No |
| `excel_row_index` | Integer | System Generated | Low | Row index in candidate spreadsheet | No |
| `confirmation_email_sent` | Boolean | System Generated | Low | `true` if confirmation email dispatched | No |
| `confirmation_email_status` | Enum | System Generated | Low | `PENDING`, `SENT`, `FAILED_RETRY` | No |

---

### C. Sales Data Model (`MODE=SALES`)

| Field Name | Type | Requirement | Sensitivity | Validation Rule | Spoken Confirmation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `lead_name` | String | Required | Low | Full name | Yes |
| `phone` | String | Required | Medium | Validated phone number | Yes |
| `email` | String | Required | Medium | Standard RFC 5322 regex | Yes |
| `company_name` | String | Required | Low | Min 2 characters | Yes |
| `requirement` | String | Required | Low | Business pain point / goal | Reflected in summary |
| `budget_range` | String | Optional | Medium | Currency / range string | Yes |
| `timeline` | String | Required | Low | Decision timeframe (e.g. 30 days)| Yes |
| `product_tier` | String | Optional | Low | Target subscription plan | Yes |
| `interest_level` | Enum | Required | Low | `HIGH`, `MEDIUM`, `LOW` | No |
| `lead_status` | Enum | Required | Low | `NEW`, `QUALIFIED`, `DEMO_REQUESTED`, etc. | Implicit |

---

### D. Customer Support Data Model (`MODE=CUSTOMER_SUPPORT`)

| Field Name | Type | Requirement | Sensitivity | Validation Rule | Spoken Confirmation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ticket_id` | String | System Generated | Low | Formatted ID (`TICK-YYYY-XXXX`) | Yes (read ticket ID) |
| `customer_name` | String | Required | Low | Full name | Yes |
| `phone` | String | Required | Medium | Validated phone number | Yes |
| `email` | String | Optional | Medium | Valid email address | Yes |
| `account_id` | String | Optional | Medium | Alphanumeric account reference | Yes |
| `category` | Enum | Required | Low | 1 of 9 defined support categories| Implicit |
| `priority` | Enum | Required | Low | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | Implicit |
| `issue_summary` | String | Required | Low | Plain language issue description | Reflected in summary |
| `troubleshooting` | String | Optional | Low | Steps completed during call | No |
| `resolution_status`| Enum | Required | Low | `RESOLVED`, `ESCALATED_TO_HUMAN`, `CALLBACK_REQUIRED` | Yes |

---

## 2. Candidate Excel Spreadsheet Schema (Future Implementation)

For recruitment workflows driven by spreadsheets, REMO binds internal session entities to explicit spreadsheet columns:

| Excel Header Column | Internal Entity Key | Expected Format | Write Behavior |
| :--- | :--- | :--- | :--- |
| **Candidate Name** | `candidate_name` | String (Alpha) | Preserved / Verified |
| **Phone Number** | `phone_number` | E.164 / 10-digit | Key identifier / Verified |
| **Email** | `email` | Valid email string | Destination for confirmation email |
| **Job Role** | `job_role` | String | Preserved / Verified |
| **Experience** | `experience_years` | Numeric / Float | Updated with caller's stated figure |
| **Skills** | `skills` | Comma-delimited list | Appended / Updated with confirmed stack |
| **Location** | `location` | String | Updated with caller's location |
| **Salary/Expected Salary** | `expected_salary`| Currency string | Updated with confirmed salary range |
| **Notice Period** | `notice_period` | String (e.g. 30 days) | Updated with confirmed availability |
| **Status** | `candidate_status` | Enum (`NEW`, `CONTACTED`, `INTERESTED`, `NOT_INTERESTED`, `SHORTLISTED`, `ON_HOLD`, `REJECTED`, `CALLBACK_REQUIRED`, `COMPLETED`)| Set based on screening outcome |
| **Notes** | `recruiter_notes` | Text | Appended with call summary and timestamp |

### Spreadsheet Integrity Directives:
- **No Column Deletion / Reordering**: REMO interacts via cell coordinates mapped to exact header strings; it never reorganizes columns or deletes worksheets.
- **Data Protection Against Overwriting**: Existing non-empty values are never overwritten with blanks if a candidate does not re-state them.
- **Pre-Write Confirmation**: Critical metrics (Notice Period, Salary, Role) must be confirmed verbally on the call before being written to the file.

---

## 3. Candidate Confirmation Email Tracking (Future Implementation)

When REMO dispatches a post-call confirmation email, the following audit attributes are tracked:
- `confirmation_email_recipient`: Verified email address of the active candidate.
- `confirmation_email_timestamp`: ISO 8601 timestamp of dispatch attempt.
- `confirmation_email_status`: `PENDING`, `SENT`, `FAILED_RETRY`.
- `confirmation_email_content_hash`: SHA-256 fingerprint of the review payload.

### Privacy Restrictions:
- Strictly scoped to the active candidate's provided email.
- Never references other candidates, interviews, or spreadsheet rows.

---

## 4. Data Retention & Privacy Considerations

1. **Storage Minimization**: Only collect fields that directly advance the active conversation task.
2. **Audio Retention**: Audio recordings must have configurable TTL (Time-To-Live), typically purged after 30 days unless retained for compliance.
3. **PII Masking**: Transcripts saved for model evaluation or analytics must pass through automated entity redaction.
4. **Right to Erasure**: Future database architectures must support `DELETE /customers/:id` cascading removal to satisfy GDPR/CCPA requests.

---

## 3. Future Relational Database Mapping Preview

```text
[organizations] 1 ────── N [agents]
                            │
                            │ 1
                            ▼ N
                         [calls] 1 ────── 1 [call_transcripts]
                            │
         ┌──────────────────┼──────────────────┐
         ▼ 1                ▼ 1                ▼ 1
    [candidates]          [leads]       [support_tickets]
         │                                     │
         ▼ N                                   ▼ N
[candidate_status_history]               [follow_ups]
```
