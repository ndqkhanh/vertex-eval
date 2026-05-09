# Vertex-Eval Block 09 — API & SDK

## Responsibility

OpenTelemetry-compatible ingestion, clean REST API, Python + TypeScript SDKs. Customers should integrate in < 30 minutes on a typical agent.

## REST API surface

Core endpoints (see [system-design.md](../system-design.md) for full list):

- `/v1/traces` — ingestion (OTel + custom).
- `/v1/rubrics` — rubric CRUD.
- `/v1/eval-runs` — submit + poll.
- `/v1/dashboards/*` — aggregated metrics.
- `/v1/lastraj/*` — federation flows.
- `/v1/alerts` — alert subscription + history.

OpenAPI spec published; client generators for other languages supported.

## OTel-compatible ingestion

Customers with existing OTel pipelines point their exporter at Vertex:

```yaml
# OTel collector config
exporters:
  otlp/vertex:
    endpoint: https://ingest.vertex-eval.example/v1/traces
    headers:
      "X-Vertex-Tenant": "acme"
      "Authorization": "Bearer ${VERTEX_API_KEY}"
```

The gateway accepts OTLP-HTTP + OTLP-gRPC; vendor-neutral.

## Python SDK

```python
from vertex_eval import Client, Trace, Rubric

client = Client(api_key=os.environ["VERTEX_API_KEY"], tenant="acme")

# Push a trace
client.traces.push(Trace(
    run_id="run-42",
    agent_name="orion-code",
    events=[...],
    audit_log_ref="s3://acme-audit/run-42.jsonl",
))

# Run an eval
rubric = client.rubrics.get("coding-agent-v3")
run = client.eval_runs.create(rubric=rubric, run_ids=["run-42"], k=3)
result = client.eval_runs.wait(run.id, timeout_s=120)

print(result.pass_pow_k, result.failure_attribution)
```

### Local-eval mode

For development, the SDK can evaluate traces locally without server round-trips (useful for regression tests in CI):

```python
from vertex_eval.local import LocalEvaluator

evaluator = LocalEvaluator(rubric=rubric, judge=MockJudge())
result = evaluator.evaluate([trace1, trace2, trace3])
```

## TypeScript SDK

Parallel API for Node / browser:

```ts
import { Client, Rubric } from "@vertex-eval/sdk";

const client = new Client({ apiKey: process.env.VERTEX_API_KEY, tenant: "acme" });
await client.traces.push({ ... });
const run = await client.evalRuns.create({ rubricId, runIds, k: 3 });
const result = await client.evalRuns.wait(run.id);
```

## Authentication

- API keys per tenant.
- Optional hardware-key-backed step-up for admin operations (rubric edits, SLA changes).
- SDK respects rate-limit headers.

## Rate limits

- Per-tenant QPS on ingestion.
- Per-API-key QPS on eval-run creation.
- Limits visible in the customer dashboard.

## Versioning

- Path-versioned (`/v1/...`).
- New major versions coexist with old for 12 months before deprecation.
- SDK versions follow semver; breaking changes bump majors.

## Failure modes

| Mode | Defense |
|---|---|
| SDK version mismatch with API | Version negotiation at connect; clear error on incompatibility |
| Network flakiness on ingestion | SDK buffers + retries with exponential backoff |
| Auth token rotation | Short-lived refresh tokens supported |
| OTLP format changes upstream | Vendor-neutral adapter layer; pin supported OTLP versions |

## Metrics

- `api.qps` per tenant
- `sdk.versions_in_use` distribution
- `api.error_rate` by endpoint
- `sdk.local_eval_usage`
- `api.deprecation_alerts_shown`
