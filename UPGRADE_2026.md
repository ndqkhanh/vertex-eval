# Vertex-Eval — May-2026 Upgrade Stub

> Companion to [`../CROSS_PROJECT_UPGRADE_PLAN_2026.md`](../CROSS_PROJECT_UPGRADE_PLAN_2026.md).
> Per the cross-project matrix, Vertex-Eval is **W1** — feeds Lyra
> L311-6 verifier-coverage index. Ship early so other bundles can use
> its Pass^k metrics.

## Headline gap (vs 2026 SOTA)

- **No `bundle/`** — Pass@k / Pass^k / judge pool not packaged for
  reuse by other harnesses.
- **Not feeding Lyra coverage** — Vertex-Eval has the metrics Lyra's
  L311-6 needs; without a bundle, the index has to compute them
  itself.
- **LLM judge pool is v1.0** — heuristic judges only at MVP; real LLM
  judges are post-bundle.

## Smallest upgrade

```text
vertex-eval/bundle/
├── bundle.yaml
├── persona.md
├── skills/
│   ├── 01-pass-at-k.md
│   ├── 02-pass-power-k.md
│   ├── 03-judge-pool.md
│   ├── 04-pii-anonymizer.md
│   ├── 05-rubric-registry.md
│   └── 06-pairwise-decorrelation.md
├── tools/
│   └── mcp_server.py          # exposes metrics + judge + rubric registry
├── memory/
│   └── seed.md                # default rubrics
├── evals/
│   ├── golden.jsonl           # ClawBench / LinuxArena slices for self-test
│   └── rubric.md
└── verifier/
    └── checker.py             # judge-human agreement check
```

## Integration with Lyra L311-6

Once installed, Vertex-Eval's MCP server exposes `record_eval(domain,
trace_id, pass)` and `compute_coverage(domain)`; the L311-6
`VerifierCoverageIndex` calls these instead of computing locally:

```python
# lyra_core/meta/verifier_coverage.py (post-bundle integration)
idx = VerifierCoverageIndex(
    backend=MCPClient("vertex-eval://record-and-compute"),
)
```

## Test plan

- 8+ tests covering bundle validation, Pass^k round-trip, judge pool
  decorrelation, PII anonymizer, and the L311-6 backend shim.

## Sequencing

W1 — early; feeds every later bundle's coverage signal.

## Related Lyra phases

- L311-4 SourceBundle — defines the bundle contract.
- L311-6 Verifier coverage — Vertex-Eval is the natural backend.
