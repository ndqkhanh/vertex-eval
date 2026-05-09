# Vertex-Eval Block 08 — Dashboards & Alerts

## Responsibility

Trajectory-first dashboards that surface the signals customers actually need — Pass^k trends, failure-class distribution, cross-channel evidence coverage, population-level decorrelation. Alerts on SLA breaches and unusual patterns.

## Core dashboards

### 1. Quality dashboard
- Pass@1 / Pass@3 / **Pass^3** trend lines.
- Confidence intervals visible.
- Stratified breakdown (easy / medium / hard).
- Per-agent / per-rubric-version toggles.

### 2. Failure-class dashboard
- Class distribution pie + trend.
- Top-5 classes this week vs last week (delta).
- Per-class sample trajectories drillable.
- Cross-class correlation heatmap (context_forget often co-occurring with plan_divergence, e.g.).

### 3. Evidence dashboard
- Cross-channel evidence level distribution.
- Trace-only vs partial vs confirmed vs contested ratio.
- Contested count (investigate each; should trend to zero).

### 4. Population decorrelation (novel)
Per the [LLN thesis in docs/53](../../../docs/53-chaos-engineering-next-era.md):
- Pairwise failure correlation across deployed agent instances.
- Goal: low correlation = population-scale reliability.
- High correlation = systemic weakness shared across instances.

### 5. Cost dashboard
- $/successful-run.
- Judge-call cost by family.
- Cost trend vs quality trend (value-per-dollar).

## Alert rules

### Hard alerts (page-worthy)
- SLA Pass^k breach sustained ≥ 3 windows.
- Safety-class attribution rate spikes > 3σ.
- Contested evidence rate > 1 %.

### Soft alerts
- Judge-human κ drops below threshold.
- Failure-class share shifts > 15 % week-over-week.
- Cost/successful-run trend reverses.

## Alert delivery

- Slack / Teams / PagerDuty / email channels (customer-configurable).
- Webhook push for customer's own SIEM.
- In-app notification log.

## Alert payload structure

```json
{
  "alert_id": "...",
  "severity": "critical" | "warning",
  "metric": "pass_pow_k",
  "observed": 0.78,
  "threshold": 0.85,
  "window": "1h",
  "trend": "degrading",
  "context": {
    "top_failure_classes": ["plan_divergence", "verification_gap"],
    "recent_regression_suspect": "rubric v7 change",
    "drill_down_url": "..."
  }
}
```

Alerts come with context; not "pass rate dropped" — "pass rate dropped to 0.78 because plan_divergence spiked".

## Trend detection

- Page-worthy alerts use robust change-point detection (avoid noise triggering).
- Soft alerts on rolling windows.
- Regression-suspect heuristic: cross-reference the breach with recent deployments / config changes.

## Customer surface

Dashboards are first-class product surface. Customers spend most of their time here after initial integration. Invested in:
- Clean URLs for sharing.
- Export to PDF for exec review.
- Embeddable panels for customer's own internal docs.
- API access to raw numbers for custom dashboards.

## Failure modes

| Mode | Defense |
|---|---|
| Alert fatigue | Tuning thresholds + change-point detection; alert-suppression for known regressions |
| Dashboard queries slow | Materialized views on common metrics; cold-tier archival for old data |
| Correlated alerts (many fire on one root cause) | Alert clustering surface; related-alerts grouping |
| Customer ignores dashboards | In-product onboarding; weekly summary email |

## Metrics (about the dashboards)

- `dashboards.views_per_tenant`
- `alerts.fires_per_day`
- `alerts.false_positive_rate` (customer-labeled)
- `alerts.mean_time_to_ack`
- `dashboards.query_latency_ms` p95
