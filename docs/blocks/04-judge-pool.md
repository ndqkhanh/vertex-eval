# Vertex-Eval Block 04 — Judge Pool

## Responsibility

Multi-family LLM pool for subjective rubric items. Per-item judge selection; different-family defaults where the agent vendor is known; local-model option for privacy tenants.

References: [docs/21 LLM-as-Judge](../../../docs/21-llm-as-judge-trajectory-eval.md), [docs/11 verifier loops](../../../docs/11-verifier-evaluator-loops.md).

## Judge families

- **Anthropic** (Claude Opus, Sonnet, Haiku variants).
- **OpenAI** (o-class, GPT variants).
- **Google** (Gemini).
- **Local** (customer-hosted for privacy — Llama-class, Qwen, DeepSeek).

Tenant configures which families are available based on contract + privacy posture.

## Per-rubric-item selection

Each rubric item can specify:
- `judge_family_pref`: "anthropic" | "openai" | "different-from-agent" | "any"
- `min_strength`: "nano" | "haiku" | "sonnet" | "opus" — required tier

Selection rules:
1. If agent vendor is known and `pref=different-from-agent`, pick a non-matching family.
2. If `pref=local` (privacy), route to local model only.
3. Tie-break: lower-cost family with sufficient strength wins.

## Judge prompt template

Every subjective item's prompt is a structured template:

```
You are an evaluator. Do not attempt to fix the artifact.

Given:
- Rubric dimension: {dimension}
- Scoring criteria: {criteria}
- Trace excerpt: {trace_excerpt}
- Cross-channel evidence (if available): {evidence}

Return strictly:
{ "score": 1-5, "evidence": "quoted trace step or audit line", "reasoning": "..." }
```

Judges are temperature 0 for determinism; `max_tokens` capped tight.

## Judge-human calibration

- Weekly: sample 50 scored items per rubric.
- Pipe to human reviewers (in-house panel or paid annotators).
- Compute Cohen's κ between judge and human.
- If κ < tenant's SLA threshold, re-tune prompt template or swap judge family.

## Bias mitigations

Per [docs/21](../../../docs/21-llm-as-judge-trajectory-eval.md):

- **Position bias** (A before B favored): randomize order on pairwise items.
- **Verbosity bias**: length-normalize when relevant.
- **Self-preference**: enforced via different-family selection.
- **Score-distribution drift**: weekly mean/variance checks.

## Structured output enforcement

Output must match the JSON schema above. Non-conforming outputs → retry once; second failure → mark item as `judge_failed`.

## Failure modes

| Mode | Defense |
|---|---|
| Judge provider outage | Failover to secondary family; tag result with `judge_family_degraded` |
| Judge drifts over time | Calibration loop; family swap when κ drops |
| Same-family assignment on agent+judge | Pref resolution catches; warning emitted |
| Cost blow-up | Per-item tier + per-eval budget caps |
| Judge hallucinates evidence | Evidence field must contain verbatim-quoted trace; post-hoc validator |

## Metrics

- `judge.calls_by_family`
- `judge.kappa_vs_human` per rubric × judge pair
- `judge.failure_rate` by family
- `judge.cost_usd` per eval run
- `judge.family_degraded_events`
