---
name: pass-at-k
description: Pass@k — fraction of tasks where ≥1 of k samples passed.
---
# Pass@k

Run a target system k times on each task. Compute Pass@k as the
fraction of tasks where at least one of the k samples passed.

Pass@k is the *capability* metric. Use it for:

- "Can the system ever solve task X?"
- "Is this task in-distribution?"

Do **not** use Pass@k for reliability claims; that's Pass^k's job.
