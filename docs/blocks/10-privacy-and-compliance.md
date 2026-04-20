# Vertex-Eval Block 10 — Privacy & Compliance

## Responsibility

Per-tenant isolation; data residency; compliance posture (SOC 2, HIPAA-on-plan, data-processing agreements). A customer sending us traces trusts us with operational internals — we honor that with clear boundaries.

## Isolation guarantees

- **Per-tenant schema or row-level isolation** in Postgres (tenant SKU determines which).
- **Per-tenant object-store prefixes** with IAM scoping.
- **No cross-tenant queries** in code paths — enforced by tenant-ID-in-connection-string and automated query review.
- **Separate encryption keys per tenant** (BYOK on SOC2+ tiers).

## Data residency

- US, EU, APAC regions.
- Tenant config pins region; requests routed and stored in-region only.
- Failover regions are within the same residency zone.

## Compliance posture

- **SOC 2 Type II** — target certification within first year.
- **ISO 27001** — on roadmap.
- **HIPAA BAA** — available on healthcare-focused plans; not default.
- **GDPR** — DPA available; right-to-erasure honored.
- **CCPA** — customer-initiated data deletion supported.

## Retention policies

- **Trace bodies**: 90 days hot, 180 days cold (archival), then purged. Customer can override retention within compliance constraints.
- **Eval results**: indefinite for aggregates; raw per-trace results follow trace retention.
- **Audit logs** (of customer access to Vertex): 7 years (compliance).
- **LaStraj contributions**: indefinite unless contributor requests removal.

## Right to erasure

- Customer issues `DELETE /v1/tenants/{id}/data/purge` with scope (`all | trace-id | run-id | user-id`).
- Platform orchestrates deletion across Postgres, object store, and replicas.
- Completion acknowledged within 30 days per GDPR.
- Purge audit log preserved (regulatory).

## PII handling

- Ingestion-time PII redactor (configurable per tenant).
- Judge calls receive redacted content by default; raw content only if explicitly opted in.
- LaStraj contributions undergo second-pass redaction.

## Customer-managed keys (BYOK)

- SOC 2+ tiers.
- Tenant supplies a KMS key ARN / resource ID.
- Vertex encrypts trace bodies + audit logs with customer-managed key.
- Tenant can revoke; all data at rest becomes unreadable.

## Subprocessor transparency

- Public list of all subprocessors (LLM providers, cloud hosts).
- 30-day notice of additions.
- Customer can veto subprocessors on regulated-industry plans.

## Supply-chain considerations

Vertex-Eval itself is an agent-system-adjacent product: it calls LLMs. Per [docs/35 malicious-intermediary](../../../docs/35-malicious-intermediary-attacks.md):

- Direct LLM provider endpoints only.
- No third-party routers without customer opt-in + transparency log.
- Response-anomaly screening on judge calls.

## Incident disclosure

- Breach notification per jurisdiction timelines.
- Customer-facing incident log with severity and affected data types.
- Post-mortems published for Sev-1 incidents (anonymized).

## Failure modes

| Mode | Defense |
|---|---|
| Cross-tenant query bug | Automated test suite + query review + defense-in-depth tenant-scoping |
| Data residency violation | Region-routing tests; periodic audit |
| PII in judge output | Reviewer samples; pattern detection |
| Subprocessor compromise | Transparency log; customer notification |
| Right-to-erasure incomplete | Purge job verifier + audit trail |

## Metrics

- `privacy.purge_requests` + completion time
- `privacy.cross_tenant_query_attempts` (should be zero)
- `privacy.region_misrouting_events`
- `compliance.subprocessor_changes`
- `compliance.audit_findings` (SOC2 / ISO)
