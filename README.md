# Vertex-Eval

**Third-party evaluation platform for AI agent systems.** Customers send traces (or run the SDK locally); Vertex returns trajectory-level scores using **cross-channel evidence** (trace + audit + state snapshot), **Pass@k and Pass^k**, **HORIZON-style failure attribution**, and a **LaStraj-federated red-team** corpus.

Design docs: [docs/architecture.md](docs/architecture.md) · [docs/architecture-tradeoff.md](docs/architecture-tradeoff.md) · [docs/system-design.md](docs/system-design.md) · [blocks/](docs/blocks/)

## MVP shape

- **Trace ingestion** — native + OTel-shaped payloads.
- **Rubric registry** — versioned rubrics + built-in check library (`task_succeeded`, `no_prompt_injection`, `no_destructive_unaudited`, `state_mutation_expected`).
- **Cross-channel evidence** — flags channels-disagree when trace/audit/snapshot evidence conflicts; `cross_channel_confirmed` only set when everything aligns.
- **Judge pool** — three heuristic judges (follower, strict-safety, latency-watchdog) voting by majority. Swap in real-LLM judges by adding functions to the pool.
- **Pass@k / Pass^k** — Pass@k via the HumanEval combinatorial estimator; Pass^k via rolling-window consecutive-success rate with `(c/n)**k` fallback.
- **HORIZON attribution** — failure classes (`task_failure`, `safety_violation`, `hallucination`, `tool_misuse`, `loop_or_stuck`, `prompt_injection`), each with a quoted step reference.
- **LaStraj federation** — PII-stripping anonymizer + content-hash dedupe; tenants contribute opt-in.
- **SLA alerts** — Pass^k floor rules return `breach=true` when observed drops below.
- **Pairwise decorrelation** — population-scale reliability metric per docs/53.
- **Privacy** — per-tenant isolation + a redactor for email/phone/card/SSN.
- **FastAPI surface** — `/v1/ingest/{native,otel}`, `/v1/evaluate`, `/v1/passk`, `/v1/sla`, `/v1/lastraj/*`, `/healthz`.

## Run locally

```bash
make install        # creates .venv, installs vendored ./harness_core + this project editable
make test           # ~48 unit tests, mock-only, no API keys required
make run            # http://localhost:8010/docs
```

Override port: `VERTEX_PORT=… make docker-up`.

## HTTP quick-taste

```bash
# 1. ingest a trace
curl -s localhost:8010/v1/ingest/native -d @trace.json -H 'content-type: application/json'

# 2. evaluate against the default rubric
curl -s localhost:8010/v1/evaluate -d '{"trace_id":"t1","rubric_id":"default_v1"}' -H 'content-type: application/json'

# 3. compute Pass^3 on a sequence
curl -s localhost:8010/v1/passk -d '{"results":[true,true,false,true,true],"k":3}' -H 'content-type: application/json'

# 4. raise alert when Pass^3 falls below 0.9
curl -s localhost:8010/v1/sla -d '{"suite":"coding","k":3,"pass_pow_k_floor":0.9,"results":[true,true,false]}' -H 'content-type: application/json'
```

## Design grounding

- Cross-channel evidence, Pass^k: `docs/38` (Claw-Eval)
- HORIZON-style attribution: `docs/27` (HORIZON)
- LLM-as-judge baseline: `docs/21`
- Decorrelation metric: `docs/53` (chaos-engineering next era)
- LaStraj corpus pattern: `docs/26` (LinuxArena)

## Status

MVP. The judge pool is heuristic; swap in real-LLM judges for production. Pass@k follows the HumanEval unbiased estimator; Pass^k is empirical-windowed.
