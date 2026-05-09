# Vertex-Eval Block 06 — HORIZON-Style Failure Attribution

## Responsibility

For every failed trajectory, assign a **failure class** with quoted step evidence. Attribution is required on every eval run; dashboards track class distribution over time.

Reference: [docs/27 HORIZON](../../../docs/27-horizon-long-horizon-degradation.md) — κ=0.84 judge-human agreement on attribution. Vertex-Eval makes this the default for every eval run.

## Failure taxonomy

Derived from HORIZON's categories, extended for production ops:

- **context_forget** — agent lost an earlier instruction / fact.
- **plan_divergence** — agent's declared plan doesn't match its actions.
- **tool_misuse** — wrong tool, wrong args, or wrong interpretation of tool output.
- **recovery_failure** — after a failure, agent doesn't recover sensibly.
- **verification_gap** — agent claims success when the outcome is not supported by evidence.
- **environment_error** — external failure (API down, quota exhausted) — not agent's fault.
- **safety_violation** — unsafe action or side effect.
- **scope_drift** — agent stepped outside authorized scope (relevant for Cipher-Sec-class).
- **rubric_ambiguity** — failure class is legitimately unclear; item surfaced for human review.

## Attribution process

For each failed eval run:

1. Classifier LLM pass (cheap model): candidate failure class.
2. Evidence-extraction pass: quote the specific trace step that reveals the failure.
3. Cross-check pass: does the evidence support the class? If not, re-classify.
4. Commit with evidence.

Rubric-item-level failures attributed separately; a trajectory can fail multiple items.

## Evidence requirement

Every attribution must include:
- `class`: the taxonomy entry.
- `evidence`: verbatim-quoted trace step.
- `step_index`: where in the trace.
- `confidence`: 0-1 score from the classifier.

Attributions without evidence → `rubric_ambiguity` (flagged for human review).

## Dashboard rollups

Daily / weekly / monthly:
- Failure class distribution per agent.
- Trend over time — did context_forget drop after the last harness upgrade?
- Top-5 failure classes this week.
- Per-stratum attribution (easy tasks rarely fail for the same reasons as hard tasks).

## Actionable output

Attribution drives engineering priority for customers:

- `context_forget` spike → invest in compaction / memory ([docs/08](../../../docs/08-context-compaction.md)).
- `verification_gap` → add verifier loop ([docs/11](../../../docs/11-verifier-evaluator-loops.md)).
- `safety_violation` → tighten hooks / permissions ([docs/05](../../../docs/05-hooks.md), [docs/06](../../../docs/06-permission-modes.md)).

Dashboards link each class to recommended harness deep-dives.

## Calibration

- Weekly: sample 50 attributions, pipe to human reviewers.
- Cohen's κ tracked per class; drops below 0.7 → retune classifier prompts.
- Customer can override an attribution; feedback improves the classifier.

## Failure modes

| Mode | Defense |
|---|---|
| Classifier biased toward one class | Distribution monitoring; drift alerts |
| Environment_error mis-attributed to agent | Evidence requirement; cross-channel check on external-call failures |
| Taxonomy extension needed | Extensible registry; new classes require reviewer approval |
| κ drops | Auto-retune; human-in-loop fallback |

## Metrics

- `attribution.classes_distribution` per tenant
- `attribution.kappa_vs_human` per class
- `attribution.ambiguity_rate` (classes requiring human review)
- `attribution.customer_override_rate`
- `attribution.class_trend_signal` (class-share delta week-over-week)
