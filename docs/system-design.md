# Vertex-Eval — System Design

## Topology

Multi-tenant SaaS with per-tenant isolation; optional self-hosted container for sensitive customers. Stateless ingestion + judging workers; stateful storage per tenant.

```
   Customer agents
   (Orion/Atlas/Syndicate/their own)
          │ OTel export / SDK push
          ▼
   ┌──────────────┐
   │   Gateway    │ — authn, rate, per-tenant routing
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Trace Store │ — append-only per tenant
   └──┬─────────┬─┘
      │         │
      ▼         ▼
 Rubric     Judge Workers
 Registry   (multi-family LLM calls)
      │         │
      └─────────┴──► Scoring Service
                          │
                          ▼
                 Failure Attribution
                          │
                          ▼
                 Dashboards + Alerts + API

  ↕ LaStraj federation (cross-tenant corpus) — opt-in
  ↕ Privacy & compliance controls
```

## Data model

```python
class Tenant:
    id: UUID
    slug: str
    region: str
    data_residency: str

class RubricVersion:
    id: UUID
    tenant_id: UUID
    name: str
    version: int
    items: list[RubricItem]    # fine-grained (Claw-Eval style)

class Trace:
    id: UUID
    tenant_id: UUID
    agent_name: str
    run_id: str
    events: list[TraceEvent]
    audit_log_ref: str | None
    state_snapshot_before: str | None
    state_snapshot_after: str | None
    ingested_at: datetime

class EvalRun:
    id: UUID
    tenant_id: UUID
    rubric_version_id: UUID
    trace_ids: list[UUID]
    k: int                     # for Pass@k and Pass^k
    status: "queued" | "running" | "complete" | "failed"

class EvalResult:
    run_id: UUID
    scores_per_trace: dict[UUID, RubricScores]
    pass_at_k: float
    pass_pow_k: float
    failure_attribution: dict[str, int]   # class → count
    cross_channel_confirmed_rate: float
    judge_family_used: dict[str, str]     # rubric_item_id → family
```

## Public API

```
POST /v1/traces                        # ingest (OTel-compatible or vendor-adapter)
POST /v1/traces/bulk                   # SDK bulk push
POST /v1/rubrics                       # create / version a rubric
GET  /v1/rubrics/{id}/versions
POST /v1/eval-runs                     # submit N traces for scoring vs a rubric
GET  /v1/eval-runs/{id}                # poll for status/result

GET  /v1/dashboards/quality            # Pass^k trend
GET  /v1/dashboards/failures           # attribution breakdown
GET  /v1/dashboards/decorrelation      # population-scale reliability

POST /v1/lastraj/contribute            # opt-in adversarial trajectory
GET  /v1/lastraj/corpus                # list vetted shared corpus

GET  /v1/alerts                        # SLA breach alerts
POST /v1/alerts/subscriptions
```

## SDK

Python and TypeScript; wraps OTel emission + SDK-local evaluation for development:

```python
from vertex_eval import Client, Rubric

client = Client(api_key=os.environ["VERTEX_API_KEY"], tenant="my-org")

# Ingest traces from production
client.traces.ingest(trace_from_my_agent(run_id, events, audit, snapshots))

# Run an eval
rubric = client.rubrics.get("coding-agent-v3")
run = client.eval_runs.create(rubric=rubric, trace_ids=trace_ids, k=3)
result = client.eval_runs.wait(run.id)

print(f"Pass^{run.k}: {result.pass_pow_k:.2f}")
print(f"Top failure class: {max(result.failure_attribution, key=result.failure_attribution.get)}")
```

## Deployment

- **Multi-tenant SaaS**: stateless API + worker pool; Postgres (per-tenant schema or shared-with-tenant-id); object store for trace bodies; Redis for queues.
- **Self-hosted**: same container distribution; single-tenant config; customer manages their own Postgres + object store.
- **Judge-worker pool**: horizontally scalable; concurrency limited per tenant per judge provider (avoid rate-limit bursts).
- **Regions**: per-tenant data residency (US, EU, APAC).

## SLOs

| Metric | Target |
|---|---|
| Trace ingestion p95 | < 100 ms acknowledge |
| Eval-run queued → first result | < 60 s for small runs; < 10 min for 1000-trace runs |
| Judge-call p95 | < 5 s |
| Dashboard refresh latency | < 2 s |
| Uptime (SaaS) | 99.9 % |
| Judge-human agreement on SLA rubrics | κ ≥ 0.80 sustained |

## Failure handling

| Failure | Response |
|---|---|
| Judge provider outage | Failover to secondary family; mark result with `judge_family_degraded=true` |
| Trace ingest backlog | Backpressure at gateway; customer alerted |
| Cross-channel evidence missing | Result tagged `evidence=trace_only`; Pass^k computed but confidence flag lowered |
| Rubric version not found | Reject eval run; customer fixes |
| LaStraj submission flagged for review | Held; contributor notified |

## Privacy & compliance

- Per-tenant isolation throughout — no cross-tenant queries possible.
- Data residency enforced per tenant.
- SOC 2 Type II target; HIPAA BAA available on plan.
- Customer-managed encryption keys option.
- Full trace delete on request (purged within 30 days across all replicas).
- LaStraj contributions require explicit opt-in per trajectory.

## Scaling

- Ingestion path stateless; scales horizontally.
- Judge workers scaled by queue depth; provider rate limits are the real ceiling.
- Trace storage: cold tier for traces >90 days (object store archival).
- Per-tenant quotas default; pay-per-use on SLA tiers.

## Roadmap post-v1

- Streaming eval (on live agent runs, not batched).
- Offline on-prem judges (local LLMs for ultra-sensitive tenants).
- Cross-tenant anonymized benchmarks (opt-in).
- ML-learned rubric tuning from customer feedback loops.

## Anti-scope

- No agent execution (not a runtime).
- No model training (not a model provider).
- No trace storage monopoly (we integrate with existing stores).
- No publishing academic benchmarks competing with researchers.
