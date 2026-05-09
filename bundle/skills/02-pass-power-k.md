---
name: pass-power-k
description: Pass^k — fraction of tasks where ALL k samples passed.
---
# Pass^k

Run k times. Compute Pass^k as the fraction of tasks where **every
one** of the k samples passed.

Pass^k is the *reliability* metric. It collapses faster than Pass@k
as k grows, which is exactly what you want — flaky systems get
exposed.

Standard report shape: Pass@1, Pass@k, Pass^k for k ∈ {1, 3, 5}.
Reading "Pass^5 = 0.42" tells you what fraction of tasks the system
*reliably* passes, not what fraction it has ever solved.

`LBL-VERTEX-PASS-POWER-K`: every reliability claim must be Pass^k.
