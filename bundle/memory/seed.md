# Vertex-Eval seed memory

## Default rubric domains

- `code` — coding-agent traces.
- `research` — research-agent traces.
- `ops` — SRE / runbook traces.
- `biomed` — biomedical agent traces (dual-use aware).
- `math` — formal-proof traces.
- `security` — defensive/offensive security traces (dual-use aware).
- `voice` — latency-critical voice traces.
- `multi-agent` — multi-agent orchestration traces (Pass^k weighted).

## Default judge pool

- `judge-correctness` — cross-channel: final + tool.
- `judge-coverage` — cross-channel: tool + state.
- `judge-safety` — cross-channel: final + state + permission_check.

(Production callers register additional judges at install time.)
