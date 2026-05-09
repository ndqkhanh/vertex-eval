# Vertex-Eval Block 01 — Trace Ingestion

## Responsibility

Accept traces from customer agents via multiple ingestion paths: OpenTelemetry export, SDK push, and vendor-specific adapters for LangSmith / Langfuse / Arize Phoenix / Anthropic tracing.

Reference: [docs/24 observability-tracing](../../../docs/24-observability-tracing.md).

## Ingestion paths

### 1. OTel export (primary)

Customer's agent emits OTel spans per the GenAI semantic conventions. Vertex-Eval's gateway accepts:
- `gen_ai.request.model`, `gen_ai.usage.*`
- Tool span attributes
- Custom attributes (tenant_id, agent_name, run_id, rubric_hint)

### 2. SDK push

Python / TypeScript SDKs batch traces and push via REST:

```python
client.traces.ingest({
    "run_id": "...",
    "agent_name": "orion-code",
    "events": [...],
    "audit_log_ref": "s3://customer/audit/...",
    "state_snapshot_before": "...",
    "state_snapshot_after": "...",
})
```

### 3. Vendor adapters

Adapters for common trace sources:
- LangSmith export JSON
- Langfuse export
- Arize Phoenix trace format
- Anthropic trace (from Anthropic's native tracing)

Each adapter maps the vendor format to Vertex's canonical trace shape.

## Canonical trace shape

```python
Trace:
  id: UUID
  tenant_id: UUID
  agent_name: str
  run_id: str
  events: list[TraceEvent]
  audit_log_ref: str | null
  state_snapshot_before: str | null
  state_snapshot_after: str | null
  ingested_at: datetime
  source_format: str
```

`TraceEvent` normalizes across vendors:

```python
TraceEvent:
  kind: "llm_call" | "tool_call" | "tool_result" | "agent_step" | "custom"
  ts: datetime
  duration_ms: int
  attributes: dict
```

## Backpressure

- Per-tenant ingestion rate cap.
- Gateway returns 429 with `Retry-After` on spike.
- SDK respects backpressure headers.

## Deduplication

Trace events deduplicated by (run_id, event_id). Repeated uploads idempotent.

## PII + sensitive-data handling

- Configurable PII redaction at ingest (per tenant).
- Secrets pattern detection; values replaced with `[REDACTED]` before storage.
- Customer can request raw-storage mode (no redaction) for full fidelity — at a compliance cost their legal team owns.

## Failure modes

| Mode | Defense |
|---|---|
| Mis-shaped trace | Schema validation at ingest; reject with structured error |
| Missing cross-channel evidence refs | Trace accepted with `evidence=partial` flag; downstream scoring adjusts |
| Vendor format drift | Adapter versioned; schema regression detection |
| PII redactor over-redacts | Tenant-level configurable patterns; regression tests |

## Metrics

- `ingest.traces_per_second` per tenant
- `ingest.schema_rejections` by reason
- `ingest.dedup_hits`
- `ingest.adapter_mix` (which source formats)
- `ingest.pii_redactions` per tenant
