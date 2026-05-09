---
name: pii-anonymizer
description: PII anonymizer — applied to every trace before judges see it.
---
# PII Anonymizer

Run every trace through the anonymizer before judges. Replaces:

- Email addresses → `<EMAIL_N>` placeholders.
- Phone numbers → `<PHONE_N>`.
- Names (best-effort regex + dictionary) → `<NAME_N>`.
- IP addresses → `<IP_N>`.
- Credit-card-pattern strings → `<CC_N>`.

`LBL-VERTEX-PII`: un-anonymized traces never reach judges.

The anonymizer is **deterministic** — the same input string always
maps to the same placeholder, so consistency across judges is
preserved.
