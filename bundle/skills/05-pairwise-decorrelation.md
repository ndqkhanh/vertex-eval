---
name: pairwise-decorrelation
description: Detect correlated judges; rotate out one of any pair >85% agreement.
---
# Pairwise Decorrelation

Maintain a per-judge-pair agreement matrix over a rolling 100-trace
window. When any pair's agreement exceeds 85% on traces with
ground-truth disagreement (i.e., the *interesting* traces), one
judge in the pair is rotated to a probation pool and a fresh judge
takes its slot.

This stops the eval from collapsing to a 1-judge system through
silent correlation drift — a common failure mode in long-running
LLM-judge installations.

Telemetry: `vertex.judge.rotated.<judge_id>` events emitted on
rotation.
