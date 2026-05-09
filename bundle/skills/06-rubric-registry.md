---
name: rubric-registry
description: Versioned rubric registry per task domain.
---
# Rubric Registry

Every domain (`code`, `research`, `ops`, `biomed`, `math`, ...) has
its own rubric, and rubrics are **versioned**. A trace's eval cites
both the rubric ID and the version that scored it.

When a rubric is updated, prior traces are *not* rescored — the
registry pins each historical eval to its rubric version so
longitudinal trend lines stay comparable.

Rubric files live in `~/.lyra/vertex/rubrics/{domain}-{version}.md`
with YAML frontmatter:

```yaml
domain: code
version: 1.2
created_at: 2026-05-09
dimensions: [correctness, coverage, safety, traceability]
weights: [0.4, 0.3, 0.2, 0.1]
```
