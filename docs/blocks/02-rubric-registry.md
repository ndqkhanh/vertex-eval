# Vertex-Eval Block 02 — Rubric Registry

## Responsibility

Versioned, per-tenant rubric library. Every eval run references a specific rubric version — if the rubric changes, a new version is created; old scores remain comparable.

Reference: [docs/21 LLM-as-Judge](../../../docs/21-llm-as-judge-trajectory-eval.md), [docs/38 Claw-Eval](../../../docs/38-claw-eval.md) (2,159 fine-grained rubric items × 300 tasks).

## Rubric schema

```yaml
id: UUID
tenant_id: UUID
name: "coding-agent-v3"
version: 4
description: "Scoring rubric for autonomous coding agents (post-Orion-Code release)."
items:
  - id: "correctness.tests_pass"
    dimension: "correctness"
    weight: 0.30
    type: "objective"        # programmatic check
    check: { kind: "tests_pass", ref: "tests/**" }

  - id: "correctness.plan_items_touched"
    dimension: "correctness"
    weight: 0.10
    type: "objective"
    check: { kind: "files_touched_subset", ref: "plan.expected_files" }

  - id: "safety.no_destructive_commands"
    dimension: "safety"
    weight: 0.20
    type: "objective"
    check: { kind: "pattern_absent", patterns: ["rm -rf", "curl *| sh", ...] }

  - id: "trajectory.path_efficiency"
    dimension: "trajectory"
    weight: 0.15
    type: "subjective"       # LLM judge
    prompt_template: "Given this trajectory, rate path efficiency 1-5 ..."
    judge_family_pref: "different-from-agent"

  - id: "faithfulness.claims_cited"
    dimension: "faithfulness"
    weight: 0.15
    type: "subjective"
    prompt_template: "Does every factual claim in the final output cite ..."
    judge_family_pref: "anthropic"
```

## Item types

- **Objective** — programmatic; deterministic; run fast; zero LLM cost.
- **Subjective** — LLM judge; per-item prompt template; judge family preference; confidence threshold.

## Versioning

- Immutable once created.
- Edits → new version.
- Eval runs reference `rubric_id + version`.
- Dashboards can diff two versions' distributions (regression signal).

## Templates

Community rubric templates for common agent classes:
- `coding-agent/basic`
- `coding-agent/claw-eval-style` (closest to the Claw-Eval 2,159-item shape)
- `research-agent/faithfulness`
- `voice-agent/latency+faithfulness`
- `security-agent/scope-compliance`
- `multi-agent/handoff-integrity`

Customers clone and tenant-specialize.

## Linting

- Weights sum to 1.0 (warning if not).
- No duplicate item IDs.
- Referenced checks exist in the check registry.
- Prompt templates pass a basic "contains evaluator instructions" check.

## Failure modes

| Mode | Defense |
|---|---|
| Rubric authored poorly | Templates + linter + human review on platform-published templates |
| Breaking-change edit in place | Immutable versions enforce; edits create new version |
| Weight sum ≠ 1 | Lint warning; runtime normalization |
| Subjective item without judge preference | Default to the tenant's preferred family |

## Metrics

- `rubric.versions_per_tenant`
- `rubric.items_distribution` (objective vs subjective)
- `rubric.template_usage`
- `rubric.lint_failures`
