---
title: Vertex-Eval — Skill quality rubrics
description: Vertex-Eval hosts a SkillsBench-style benchmark for skill-evolution evaluation.
---

# Vertex-Eval — Skill-quality rubrics

Vertex-Eval doesn't *consume* skills — it *measures* them. This integration
adds a `skill_quality` rubric category with checks that score per-skill
trust tier, provenance presence, cross-model audit, and held-out eval
performance.

## Corner of the design space

| Axis | Value |
|---|---|
| Role | Benchmark host |
| Skill artifact | Reads any harness_skills `SkillRecord` |
| Parameter access | n/a |
| Reference paper | All four 2026 papers — Vertex serves all four corners. |

## Adapter

`vertex_eval.skills_rubric` provides:

- `score_trust_tier_correct(record)` → `True` if tier matches source kind.
- `score_provenance_present(record)` → `True` if all v2.1 fields present.
- `score_content_hash_present(record)` → `True` if `sha256` is computed.
- `score_skill_record(record)` → aggregate score in [0, 1].

## Bright-lines

- `BL-VERTEX-SKILL-LEAK` — skill content excluded from federated traces
  unless tenant explicitly opts in.
