# Vertex-Eval eval rubric

A trace eval **passes** when:

1. The judge pool's aggregated `correctness` score matches the
   ground-truth label (within ±0.05 tolerance).
2. The reported Pass^k matches the expected `expected_pass_power_3`
   (when k=3 is available).
3. PII anonymization stripped every entry the redactor's heuristics
   flagged (zero leak rate).

Aggregate metrics:

- **Judge–human agreement** — Spearman correlation between
  aggregated judge score and ground-truth label.
- **Pass^k recovery** — fraction of traces whose Pass^k matches
  expectation across k ∈ {1, 3, 5}.
- **Decorrelation health** — number of judge pairs with >85%
  agreement on disagreement-traces in the rolling window.
- **PII leak rate** — fraction of judged traces with un-redacted PII
  (target: 0).
