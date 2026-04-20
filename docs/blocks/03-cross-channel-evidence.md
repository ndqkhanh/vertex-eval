# Vertex-Eval Block 03 — Cross-Channel Evidence

## Responsibility

Triangulate evaluation across three independent channels — **trace**, **audit log**, **environment snapshot** — so agent output labeled "successful" is confirmed by the environment, not only by the agent's self-report. This is the core product thesis: trajectory-opaque eval misses 44 % of safety violations ([docs/38 Claw-Eval](../../../docs/38-claw-eval.md)).

## The three channels

### 1. Trace
The agent's own record: events, LLM calls, tool calls, decisions. Delivered via ingestion ([block 01](01-trace-ingestion.md)).

### 2. Audit log
An independent record from a system that is not the agent. Examples:
- Aegis-Ops style signed audit log.
- Cloud platform audit (CloudTrail, GCP audit logs, K8s audit).
- Downstream service logs (database write log, Slack API audit).

### 3. Environment snapshot
Before / after hashes of the target resources the agent touched. The platform computes the diff.

## Confirmation levels

- **Confirmed** — all three channels agree on the claimed outcome.
- **Partial** — two channels agree; the third is missing or ambiguous.
- **Contested** — channels disagree (possible sabotage, bug, or instrumentation error).
- **Trace-only** — no audit + no snapshot available; only the agent's self-report.

Scoring results carry a `evidence_level` field; dashboards surface distributions.

## Evidence-level policies

- **SLA-grade rubric items** (safety, compliance) require `confirmed` or `partial`; `trace-only` disqualifies the result for SLA.
- **Development rubrics** accept all levels with surface annotations.
- **LaStraj corpus contributions** require `confirmed` to count.

## Why this matters in numbers

[Claw-Eval](../../../docs/38-claw-eval.md) reports:
- Trajectory-opaque evaluation misses **44 %** of safety violations.
- Cross-channel evidence recovers most of that gap.

Vertex-Eval's primary selling point is making this discipline operational for customers who can't run their own Claw-Eval pipeline in-house.

## Integration paths

Customers supply audit logs / snapshots via:
- Cloud audit export to an S3 bucket Vertex reads.
- Webhook push.
- SDK side-channel upload alongside traces.
- Connector modules for common platforms (AWS, GCP, Azure, K8s).

## Privacy

- Audit logs and snapshots may contain sensitive content. Stored per-tenant with encryption at rest.
- Redactor applied to snapshot diffs before judge calls.
- Customer can opt for "judge sees hash-only" for extreme sensitivity (weaker eval but maximum privacy).

## Failure modes

| Mode | Defense |
|---|---|
| Audit log lagging behind trace | Eval queued until audit window catches up or timeout → `partial` |
| Snapshot too large for judge context | Structured diff summary; full diff retained for drill-down |
| Contested channels (agent says X, env says Y) | Escalate to human review queue; surface prominently |
| Tenant missing cross-channel instrumentation | Trace-only acceptable for non-SLA items |

## Metrics

- `evidence.level_distribution` per tenant
- `evidence.contested_count` (critical — investigate each)
- `evidence.audit_lag_p95`
- `evidence.sla_disqualification_rate` (trace-only on SLA items)
