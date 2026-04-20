# Vertex-Eval — Architecture Trade-offs

## Trade-off 1: Pass^k SLA vs Pass@k best-effort

**Chosen:** Pass^k as the default SLA contract.

**Alternative:** Pass@k (any-of-k-succeeds).

**Why:** Pass@k is generous — customers want reliability, not lucky runs. Pass^k (every-of-k-succeeds) captures consistency, which is what production deployments actually need. [Claw-Eval](../../docs/38-claw-eval.md) introduced Pass^k as a metric; we treat it as a contract.

**Cost:** Harder number to hit; customers initially uncomfortable. Education path: we report both.

## Trade-off 2: Multi-family judge pool vs single-vendor

**Chosen:** Multi-family — Anthropic + OpenAI + local model options per rubric.

**Alternative:** Single vendor across all evals.

**Why:** Shared-blind-spot bias is real. Different-family judges reduce correlated miss rates on the evaluated agents. Per-rubric selection lets us pick the judge best-suited to each dimension.

**Cost:** Multi-vendor integration. Standard.

## Trade-off 3: Cross-channel evidence required vs trace-only

**Chosen:** Customers must supply (or opt in to platform collection of) audit logs + snapshots alongside traces for "cross-channel confirmed" labeling.

**Alternative:** Trace-only; produce weaker labels.

**Why:** The [44 % safety-violation recall gap](../../docs/38-claw-eval.md) in trajectory-opaque eval is the whole product thesis. Without cross-channel evidence we are another tracing product.

**Cost:** More customer integration work. Mitigated by SDK helpers + recommended ingestion patterns.

## Trade-off 4: SaaS + self-hosted hybrid vs SaaS only

**Chosen:** Multi-tenant SaaS default + self-hosted option for sensitive customers.

**Alternative:** Pure SaaS.

**Why:** Pentest customers, regulated-industry customers, and some enterprise customers refuse to ship traces off-premises. Self-hosted is a customer-unlock feature with real demand.

**Cost:** Two deployment paths to support. We ship a single containerized distribution that supports both with config flips.

## Trade-off 5: HORIZON attribution required vs optional

**Chosen:** Required on every run.

**Alternative:** Opt-in.

**Why:** Failure attribution changes how customers iterate. Making it always-on drives product value; opt-in hides the signal.

**Cost:** Extra judge calls. Mitigated by nano-tier models where class inference doesn't need a strong judge.

## Trade-off 6: LaStraj federation opt-in vs automatic

**Chosen:** Strictly opt-in; customer must explicitly contribute each trajectory.

**Alternative:** Automatic (any adversarial-looking trajectory auto-shared).

**Why:** Privacy. Adversarial trajectories may contain sensitive target information. Explicit opt-in is the only tenable default.

**Cost:** Slower corpus growth; worth it.

## Trade-off 7: Rubric versioning is a hard requirement

**Chosen:** Every rubric has a version; eval runs reference a specific version.

**Alternative:** Rubrics are editable in place.

**Why:** Benchmark numbers change when rubrics change; without versioning, trends are uninterpretable.

**Cost:** Versioning infra. Standard.

## Trade-off 8: Scoring as judgment + evidence vs judgment only

**Chosen:** Every score includes evidence (quoted trace step, quoted audit log line).

**Alternative:** Score + rationale prose only.

**Why:** Auditability. Customers need to trust the scores; quoted evidence is a much stronger artifact than "the judge says so."

**Cost:** More storage + more judge-output structure. Worth it.

## Trade-off 9: Synchronous vs asynchronous eval

**Chosen:** Async by default; customers don't block on eval results.

**Alternative:** Sync — customer waits on each eval.

**Why:** Judge calls + cross-channel evidence fetching are slow (seconds to minutes). Async ingest-and-score is the right shape; webhooks / polling for results.

**Cost:** Async UX complexity. Standard practice for eval SaaS.

## Trade-off 10: Judge-human calibration required vs optional

**Chosen:** Required for SLA-grade customers; optional for low-tier.

**Alternative:** Optional for all.

**Why:** Judge drift is real; customers paying for SLA guarantees need calibration proof. Weekly human-labeled samples + Cohen's κ tracking.

**Cost:** Human-labeler budget. Passed through as part of SLA pricing.

## Rejected alternatives

- **Host agents ourselves to run the evals.** We eval — we don't run. Keeps us neutral.
- **Build our own benchmark suite.** We consume public benchmarks (SWE-bench, miniF2F, BixBench, LinuxArena, ClawBench); the LaStraj federation is additive.
- **Train our own judge fine-tune.** Stay provider-agnostic. Better judges are a prompting + selection problem, not training.
- **Open-source everything.** Some components open (SDK, rubric templates); the platform itself closed-source to maintain quality control.
