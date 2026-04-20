# Vertex-Eval — Architecture

## What Vertex-Eval is

Vertex-Eval is a **third-party evaluation platform** for AI agent systems, SaaS-delivered. Customers send traces (or run the evaluation locally against our SDK), and Vertex returns trajectory-level scores using **cross-channel evidence** (trace + audit log + state snapshot), **Pass@k and Pass^k**, **HORIZON-style failure attribution**, and a **LaStraj-federated red-team suite** — the methodology demonstrated in [Claw-Eval](../../docs/38-claw-eval.md) and [HORIZON](../../docs/27-horizon-long-horizon-degradation.md) packaged as a service.

This is Syndicate's counterpart: Syndicate orchestrates agent workflows; Vertex-Eval evaluates them.

## Honest baselines

| Baseline | Reported number / shape |
|---|---|
| **Claw-Eval** (arXiv:2604.06132) | 2,159 fine-grained rubric items × 300 human-verified tasks; 3 evidence channels; **trajectory-opaque evaluation misses 44 % of safety violations** ([docs/38](../../docs/38-claw-eval.md)) |
| **HORIZON** (arXiv:2604.11978) | Trajectory-grounded LLM-as-Judge with **κ = 0.84** vs human annotators; failure-class attribution taxonomy ([docs/27](../../docs/27-horizon-long-horizon-degradation.md)) |
| **LLM-as-Judge** literature | Zheng et al. 2023 and follow-ups; judge-human agreement depends heavily on rubric quality ([docs/21](../../docs/21-llm-as-judge-trajectory-eval.md)) |
| **LangSmith / Langfuse / Arize Phoenix** | Trace storage + simple evaluators; not trajectory-first; no Pass^k SLA; no cross-channel evidence by default |
| **ClawBench** (arXiv:2604.08523) | Live web benchmark; Claude Sonnet 4.6 at 33.3 % ([docs/34](../../docs/34-clawbench-live-web-tasks.md)) |

## Design targets (hypotheses)

- **Pass^k as SLA.** Customers express quality commitments in Pass^3 / Pass^5 — stricter than Pass@k — and Vertex reports against that contract. **Assumption:** Pass^k captures "consistency" better than Pass@k for production-grade reliability.
- **Cross-channel recall.** Recover the ~44 % of safety violations that trajectory-opaque eval misses, using the trace + audit + snapshot triangulation ([docs/38](../../docs/38-claw-eval.md)).
- **Judge-human agreement.** Match or approach HORIZON's κ = 0.84 on a new task class within 30 days of onboarding, using rubric-versioning + human calibration loop.
- **Federated red-team corpus.** Grow a community LaStraj-class corpus across tenants (opt-in, anonymized) to create a credible public agent-security benchmark.

## Component diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                            Vertex-Eval                               │
│                                                                      │
│   Customer agent / trace → [Trace Ingestion]                         │
│                                │                                     │
│                                ▼                                     │
│                       [Rubric Registry]                              │
│                                │                                     │
│                                ▼                                     │
│                    [Cross-Channel Evidence]                          │
│                    trace + audit + snapshots                         │
│                                │                                     │
│                                ▼                                     │
│                      [Judge Pool (multi-family)]                     │
│                                │                                     │
│                     ┌──────────┼──────────┐                          │
│                     ▼          ▼          ▼                          │
│                 [Pass@k]  [Pass^k]  [HORIZON failure attribution]    │
│                                │                                     │
│                                ▼                                     │
│                  [LaStraj red-team federation]                       │
│                                │                                     │
│                                ▼                                     │
│               [Dashboards + alerts + API/SDK]                        │
│                                                                      │
│   ↕ Privacy + compliance (per-tenant isolation)                      │
└──────────────────────────────────────────────────────────────────────┘
```

## The ten architectural commitments

1. **Trace ingestion** — OpenTelemetry + vendor-specific adapters (LangSmith, Langfuse export, Anthropic trace, Helicone). See [blocks/01-trace-ingestion.md](blocks/01-trace-ingestion.md).
2. **Rubric registry** — versioned, per-tenant rubrics; community rubric templates. See [blocks/02-rubric-registry.md](blocks/02-rubric-registry.md).
3. **Cross-channel evidence** — first-class triangulation across trace + audit log + environment snapshot. See [blocks/03-cross-channel-evidence.md](blocks/03-cross-channel-evidence.md).
4. **Judge pool** — multi-family LLMs (Anthropic, OpenAI, local); judge selection per rubric item. See [blocks/04-judge-pool.md](blocks/04-judge-pool.md).
5. **Pass@k and Pass^k scoring** — first-class metrics, not afterthought. Pass^k as SLA contract. See [blocks/05-passk-metrics.md](blocks/05-passk-metrics.md).
6. **HORIZON-style failure attribution** — classify every failed trajectory into a failure class with quoted step evidence. See [blocks/06-failure-attribution.md](blocks/06-failure-attribution.md).
7. **LaStraj red-team federation** — opt-in anonymized adversarial trajectories shared across tenants. See [blocks/07-lastraj-federation.md](blocks/07-lastraj-federation.md).
8. **Dashboards + alerts** — trajectory-first dashboards; alert on Pass^k regressions. See [blocks/08-dashboards-alerts.md](blocks/08-dashboards-alerts.md).
9. **API + SDK** — OTel-compatible ingestion; Python/TS SDKs for local eval runs. See [blocks/09-api-and-sdk.md](blocks/09-api-and-sdk.md).
10. **Privacy + compliance** — per-tenant isolation; SOC2/ISO-ready posture; data residency. See [blocks/10-privacy-and-compliance.md](blocks/10-privacy-and-compliance.md).

## Novel contributions (not present in cited systems)

1. **Pass^k as a service-level contract.** Claw-Eval introduced Pass^k as a metric; Vertex-Eval turns it into a **product SLA**: a customer can purchase "Pass^3 ≥ 0.85 on this benchmark suite" and get alerts when the production agent fails to meet it. First productization of Pass^k.

2. **Cross-channel evidence as third-party API.** Third-party eval platforms today (LangSmith, Langfuse, Arize Phoenix) score traces in isolation. Vertex-Eval requires audit log + state snapshot *alongside* trace to produce a "cross-channel confirmed" label — operationalizing Claw-Eval's discipline for production eval.

3. **Decorrelation metrics from LLN thesis.** Per the [chaos-engineering thesis](../../docs/53-chaos-engineering-next-era.md), population-scale reliability depends on decorrelation between agent failures. Vertex-Eval measures pairwise failure correlation across deployments and exposes "population decorrelation" as a dashboard metric — novel and essential for customers running many agent instances.

4. **LaStraj red-team federation.** Customers contribute anonymized adversarial trajectories to a shared corpus. This creates the cross-tenant agent-security benchmark that doesn't currently exist. Attribution is optional; contributions are vetted by platform reviewers. Directly builds on [LinuxArena's LaStraj](../../docs/26-linuxarena-production-agent-safety.md) insight as shared infrastructure.

5. **HORIZON failure attribution as first-class product.** HORIZON showed κ=0.84 on a curated dataset; Vertex-Eval makes the attribution pipeline a default for every evaluation run, with a dashboard that tracks which failure class dominates this week vs last week — turning research methodology into operational signal.

## Non-goals

- Not an agent runtime (Syndicate / Deep Agents / OpenClaw do that).
- Not a trace storage service alone (LangSmith / Langfuse do that — we consume their exports).
- Not a model provider (we route to Anthropic / OpenAI / local for judge calls).
- Not a benchmark publisher competing with academic evals (we run third-party evals against those benchmarks).

## Cross-references

- Trade-offs: [architecture-tradeoff.md](architecture-tradeoff.md)
- Operations: [system-design.md](system-design.md)
- Research: [docs/21](../../docs/21-llm-as-judge-trajectory-eval.md), [docs/27](../../docs/27-horizon-long-horizon-degradation.md), [docs/38](../../docs/38-claw-eval.md), [docs/34](../../docs/34-clawbench-live-web-tasks.md), [docs/24](../../docs/24-observability-tracing.md), [docs/26](../../docs/26-linuxarena-production-agent-safety.md), [docs/53](../../docs/53-chaos-engineering-next-era.md).

## Status

Design specification, April 2026. Scaffold-quality. Not implemented. Target environment: multi-tenant SaaS with per-tenant isolation + optional self-hosted deployment for sensitive customers.
