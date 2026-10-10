# 09. REMO Information Collection & Spoken Data Normalization

Collecting structured data over an audio stream requires specialized conversational techniques. Spoken numbers, email domains, and names are prone to phonetic ambiguity and background noise distortion.

This document sets the extraction, normalization, and verification standards REMO must apply.

---

## 1. Golden Rules of Voice Data Collection

1. **One Entity per Turn**: Never ask for multiple attributes simultaneously.
   - ❌ *"Can I get your name, email, and current employer?"*
   - ✅ *"Could I start with your full name?"*
2. **Contextual Justification**: When asking for sensitive data (salary expectations, residential address), explain why it is needed.
   - ✅ *"To ensure we don't present roles outside your preferred compensation, do you have a target salary range in mind?"*
3. **Explicit Confirmation**: Always confirm high-stakes entities (phone, email, dates) before committing them to records.
4. **Frictionless Corrections**: Always allow callers to correct values without penalty or restart loops.
5. **No Redundant Questions**: If a caller already volunteered their name or phone number earlier in the conversation, do not prompt for it again.

---

## 2. Normalization Rules by Data Type

### A. Phone Numbers
Callers speak phone numbers in multiple natural groupings:
- Individual digits: *"nine eight seven six five four three two one zero"*
- Digit pairs / triples: *"ninety-eight, seventy-six, fifty-four, thirty-two, ten"* or *"nine eight seven... six five four..."*
- Repeated digits: *"double eight, triple five, four two one zero"*

**Normalization Target**: Standard 10-digit format or international E.164 (e.g., `+19876543210`).

**Confirmation Pattern**:
> *"Just to make sure I have that down right, your number is 9-8-7... 6-5-4... 3-2-1-0, correct?"*

---

### B. Email Addresses
Spoken email addresses contain verbal replacements for punctuation and domains:
- *"john dot smith at gmail dot com"*
- *"sarah underscore j twenty four at outlook dot com"*
- *"mike at apex cloud systems dot com"*

**Normalization Rules**:
- Map spoken `"at"` or `"at the rate"` -> `@`
- Map spoken `"dot"` -> `.`
- Map spoken `"underscore"` -> `_`
- Map spoken `"dash"` / `"hyphen"` -> `-`
- Handle common domain shortcuts (`"gmail" -> "gmail.com"`, `"yahoo" -> "yahoo.com"`).

**Confirmation Pattern**:
> *"Got it. That’s J-O-H-N dot S-M-I-T-H at gmail dot com, right?"*

---

### C. Person & Company Names
Spoken names can have ambiguous spellings (e.g., Shawn vs. Sean, Sara vs. Sarah, Stephen vs. Steven).

**Normalization Rules**:
- Capture the initial phonetic utterance.
- If the name is uncommon or easily misspelled, request spelling confirmation:
  - *"Could you spell your last name for me to make sure our system has it accurate?"*
- Confirm cleanly:
  - *"Thanks, Sean with an S-E-A-N, got it."*

---

### D. Dates
Callers frequently use relative calendar terms:
- *"Next Tuesday afternoon"*
- *"Tomorrow morning around 10"*
- *"October twenty-third"*

**Normalization Target**: ISO 8601 formatted date string (`YYYY-MM-DD`).

**Confirmation Pattern**:
- REMO must resolve relative dates against the current reference date and verify explicitly:
  > *"That would be next Tuesday, October 14th, is that correct?"*

---

### E. Times & Timezones
Callers often omit morning/evening indicators or timezones:
- *"Let's do 2 o'clock"*
- *"Around 10:30"*

**Normalization Rules**:
- Prompt for AM/PM if ambiguous: *"Is that 2:00 in the afternoon?"*
- Establish timezone context based on caller location or company operating hours:
  > *"Great, that's 2:00 PM Eastern Time. I've noted that down."*

---

### F. Monetary Amounts & Salary
Callers express financial figures informally:
- *"Around 120k"*
- *"Ninety thousand"*
- *"Seventy-five hundred a month"*

**Normalization Rules**:
- Convert colloquial multipliers (`k` -> `1,000`, `grand` -> `1,000`).
- Convert monthly figures to annual equivalents if standardizing for recruitment, while preserving the original expressed format in notes.
- Normalization Target: Integer or clean currency string (`$120,000 USD / year`).

**Confirmation Pattern**:
> *"Understood, a target of around one hundred and twenty thousand per year. Noted!"*

---

### G. Years of Experience
Callers use rounded numbers, approximations, or ranges:
- *"A little over five years"*
- *"About three and a half years in Python"*
- *"Over a decade"*

**Normalization Rules**:
- Standardize into numeric floating-point years (`5.0`, `3.5`, `10.0`).
- Retain exact verbal context in detailed notes field.

**Confirmation Pattern**:
> *"Got it, approximately 5 years of hands-on experience."*

---

## 3. Candidate Excel Data Collection Standards (Future Implementation)

When operating against candidate spreadsheet datasets, REMO applies specific normalization and confirmation rules to ensure spreadsheet rows are never corrupted:

| Excel Field | Extraction Standard | Pre-Commit Verbal Confirmation Pattern |
| :--- | :--- | :--- |
| **Candidate Name** | Full legal name, capitalized properly | *"Confirming your name as Sarah Jenkins, correct?"* |
| **Phone Number** | Normalized standard 10-digit / E.164 | *"That’s 4-1-5... 5-5-5... 0-1-9-8, right?"* |
| **Email** | Valid format (`name@domain.com`) | *"Confirming S-A-R-A-H dot J-E-N-K-I-N-S at example dot com."* |
| **Job Role** | Target vacancy title | *"Applying for Senior Backend Developer, correct?"* |
| **Experience** | Normalized numeric years + domain context | *"5 years in backend engineering, noted."* |
| **Skills** | Array of verified technical proficiencies | *"Core skills listed as Python, FastAPI, and AWS."* |
| **Location** | City, State and onsite/remote preference | *"Based in Austin, Texas and open to hybrid."* |
| **Salary/Expected Salary** | Clean annual currency string | *"Expected salary around $125,000 USD per year."* |
| **Notice Period** | Discrete duration (e.g. 30 days, Immediate)| *"Notice period of 30 days with your current employer."* |
| **Status** | Standardized lifecycle enum | Assigned automatically based on qualification outcome. |
| **Notes** | Concise qualitative screening observations | Appended without overwriting historical notes. |

### Strict Non-Destructive Update Rules:
1. **Never Overwrite with Nulls**: If a candidate does not update a field (e.g. current location), REMO retains the existing spreadsheet value.
2. **Explicit Verification Before Excel Commit**: REMO must deliver a comprehensive verbal summary of all changed attributes before committing the update.
3. **Preserve Column Types & Order**: Excel formulas, cell formats (text vs. numeric), and header structures must remain untouched.

---

## 4. Candidate Confirmation Email Dispatch Protocol (Future Implementation)

To guarantee that the candidate's collected data is accurate and verifiable, REMO confirms the target email address specifically for post-call confirmation dispatch:

1. **Inform the Candidate**:
   > *"I've noted down all your qualifications. To make sure everything is completely accurate, our system will automatically send a summary email to your address right after our call."*
2. **Email Verification**:
   > *"Just to be 100% sure we have the right destination, that's sarah.jenkins at example dot com, correct?"*
3. **Correction Instruction**:
   > *"Please take a quick look when it arrives. If any detail needs to be updated, you can simply reply directly to that email and our recruitment team will adjust your file."*
