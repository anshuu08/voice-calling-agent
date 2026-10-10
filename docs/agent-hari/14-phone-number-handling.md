# 14. REMO Spoken Phone Number Normalization & Verification

Phone numbers represent one of the most critical and error-prone entities captured over voice channels. Callers speak in varied rhythms, use colloquial counting terms ("double eight"), mix country codes, pause midway, and correct themselves.

This document sets the operational standards for capturing and verifying phone numbers with 100% accuracy.

---

## 1. Supported Spoken Input Variations

REMO must accurately parse all of the following conversational patterns:

| Pattern | Caller Utterance | Normalized Value |
| :--- | :--- | :--- |
| **Digit by Digit** | *"four one five... five five five... zero one nine eight"* | `4155550198` |
| **Grouped Pairs & Triples** | *"four fifteen... five fifty-five... zero one ninety-eight"* | `4155550198` |
| **Indian 5-5 Format** | *"nine eight seven six five... four three two one zero"* | `9876543210` |
| **Repeated Digit Multipliers**| *"triple eight... double two... zero nine"* | `8882209` |
| **With Country Code** | *"plus one... nine one seven... five five five... twelve twelve"* | `+19175551212` |
| **International Spoken** | *"plus four four... seven nine one one... double zero double zero zero zero"* | `+447911000000` |

---

## 2. Multi-Part / Interrupted Number Capture

Callers often break numbers into multiple conversational turns:

- **Caller**: *"It’s nine eight seven... six five..."*
- **REMO**: *"Got the first five digits: 9-8-7-6-5. What are the remaining numbers?"*
- **Caller**: *"Four three two one zero."*
- **REMO**: *"Great! Let me confirm the full number: that's 9-8-7-6-5-4-3-2-1-0. Did I get that right?"*
- **Caller**: *"Yes, that's it."*

---

## 3. Strict Rule: Never Assume Missing Digits

> [!WARNING]
> If a caller provides fewer digits than the standard national or international format requires (e.g., providing 9 digits instead of 10 for a US or Indian number), REMO must **NEVER** guess or auto-complete the missing digit.

- **Bad**: Assuming a missing leading `0` or trailing `0`.
- **REMO**: *"It sounds like that number was 9 digits long. Could you repeat all 10 digits for me just to make sure we don't miss you?"*

---

## 4. Mid-Utterance Self-Corrections

Callers frequently catch mistakes while speaking:

- **Caller**: *"My number is 555-0198... wait, no, sorry, that’s my old office number. It’s 555-0144."*
- **Handling Rule**: The parsing engine must clear the initial buffer upon detecting negation cues (*"wait"*, *"no"*, *"sorry"*, *"cancel that"*, *"my new number is"*) and lock onto the revised sequence.
- **REMO Response**: *"Got it, switching to 5-5-5... 0-1-4-4. And what’s the area code for that?"*

---

## 5. Verification Phrasing Standard

When reading back numbers, REMO must use **rhythmic acoustic chunking** (3-3-4 for North American numbers; 5-5 for Indian numbers):

### North American Number Pattern:
> *"Just to verify, that’s area code 4-1-5... 5-5-5... 0-1-9-8, correct?"*

### Indian Mobile Number Pattern:
> *"Just confirming your mobile number: 9-8-7-6-5... 4-3-2-1-0, correct?"*

### International Number Pattern:
> *"Just to confirm the country code and number: plus 4-4... 7-9-1-1... 0-0-0-0-0-0, is that right?"*
