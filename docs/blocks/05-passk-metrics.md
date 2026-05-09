# Vertex-Eval Block 05 — Pass@k and Pass^k Metrics

## Responsibility

Compute and surface both Pass@k (any-of-k succeeds) and **Pass^k (every-of-k succeeds)** as first-class metrics. Pass^k is the primary SLA contract.

Reference: [docs/38 Claw-Eval](../../../docs/38-claw-eval.md) — which introduced Pass^k and showed that peak performance stays stable while Pass^3 drops up to 24% on error-injection tests, revealing consistency as the binding constraint.

## Definitions

Given `k` independent runs on the same task:

- **Pass@k** = probability at least one of the `k` runs passes.
- **Pass^k** (Pass-to-the-k) = probability all `k` runs pass.

Pass@k is generous; Pass^k is strict. For production, Pass^k is what reliability actually means.

## Why Pass^k as SLA

A customer deploying an agent cares about **consistency** — every user turn should meet the quality bar. "My agent passes 1-in-4 times" isn't a production signal. Pass^3 on a stratified workload set aligns with real product experience.

## Stratified-workload sampling

Pass^k computed over:
- A customer-supplied workload definition (balanced across task classes).
- Or a published benchmark (miniF2F, SWE-bench Verified, ClawBench, LinuxArena).
- Or the LaStraj federation corpus (adversarial class).

Default `k=3`. SLA customers can negotiate k=5.

## SLA contract shape

```yaml
tenant: acme
agent_name: orion-code-prod
rubric_version: coding-agent-v3@7
workload: claw-eval-suite@2
sla:
  metric: pass_pow_k
  k: 3
  threshold: 0.85
  evaluation_cadence: "every 1h on rolling 1000 runs"
  breach_action: alert(slack_channel="#ops")
```

Breach alerts include: current Pass^k, trend, top failure-attribution classes.

## Reporting format

Every eval run's result includes:

```json
{
  "pass_at_1": 0.71,
  "pass_at_3": 0.85,
  "pass_pow_3": 0.42,         // the strict one
  "sample_size": 300,
  "task_strata": { "easy": 120, "medium": 120, "hard": 60 },
  "per_stratum_pass_pow_3": { "easy": 0.71, "medium": 0.38, "hard": 0.08 }
}
```

## Confidence intervals

Pass^k on small samples is noisy. Every published number includes a Wilson score interval. Dashboards show the interval, not just the point estimate.

## Anti-gaming

- Customer cannot silently rerun failed traces until pass. Traces are immutable once ingested; Pass^k sees the actual population.
- Cross-channel evidence level ([block 03](03-cross-channel-evidence.md)) filters: `trace-only` results don't count toward SLA Pass^k.

## Failure modes

| Mode | Defense |
|---|---|
| Small sample → wide CI | Surface CI on all numbers; require min-N for SLA claims |
| Stratum imbalance | Workload registry enforces declared strata balance |
| Customer gaming via rerun-till-pass | Immutable trace ingestion; eval over the population |
| Pass^k alerts too noisy | Rolling-window smoothing; breach requires K consecutive windows |

## Metrics

- `passk.pass_at_k` distribution
- `passk.pass_pow_k` distribution
- `passk.ci_width` (measure of how confident our numbers are)
- `passk.sla_breach_events`
- `passk.breach_to_resolve_time`
