# Vertex-Eval Block 07 — LaStraj Red-Team Federation

## Responsibility

Maintain a **shared, cross-tenant adversarial-trajectory corpus** — opt-in, anonymized, reviewer-vetted. Customers can contribute adversarial trajectories from their own engagements; the shared corpus becomes a cross-industry benchmark for agent-security monitors.

Reference: [docs/26 LinuxArena / LaStraj](../../../docs/26-linuxarena-production-agent-safety.md), [docs/49 Agents of Chaos](../../../docs/49-agents-of-chaos-red-teaming.md).

## Why federation

LaStraj's finding: human-crafted adversarial trajectories evade model-based monitors at much higher rates than auto-generated attacks. A *shared* corpus is the only way to build a benchmark that covers the long tail of human creativity.

Today no such cross-tenant corpus exists publicly. Vertex-Eval's federation is the first attempt to build one as community infrastructure while respecting customer privacy.

## Contribution flow

1. Customer submits a trajectory via `POST /v1/lastraj/contribute` with:
   - Anonymized trace.
   - Declared attack class.
   - Declared target technique.
   - Whether it succeeded (against whose monitor).
   - Legal clearance flag (customer confirms they have the right to share).
2. Platform reviewers vet:
   - Schema validity.
   - Novelty (not a duplicate of an existing corpus entry).
   - Safety — does publishing the trajectory enable harm? (some attacks are too recipe-like).
3. Accepted → added to the shared corpus with version tag + attribution (optional).

## Attribution

- Optional. Default is anonymous.
- Customers who contribute and opt in get credit on the corpus page.
- Academic contributors may want citation; contribution UI supports structured attribution.

## Corpus versioning

- Tagged releases (monthly cadence).
- Each release has a changelog.
- Evaluation results should always cite a corpus version.

## Corpus usage

Tenants can:
- **Run their monitor / agent against the corpus** to see evasion rate.
- **Subscribe to updates** for continuous regression testing.
- **Download anonymized copies** for in-house use.

Industry benchmarks published quarterly: "Median evasion rate across N subscribed agents on LaStraj corpus v12".

## Safety and moderation

Some trajectories are too dangerous to publish (e.g., working exploits for zero-day vulnerabilities). Moderation rules:

- Trajectories targeting specific patched-but-recent CVEs: held until CVE is sufficiently old.
- Trajectories that include working credential exfil paths: never public; usable for customer's private monitor tuning only.
- Trajectories revealing proprietary target infrastructure: always refused.

## Categories covered

- Prompt-injection via tool output.
- Credential exfiltration.
- Persistence planting.
- Cross-scope pivot.
- Supply-chain injection.
- Social engineering / authority confusion.
- Role-confusion (defender / attacker mix).
- False-success reporting.

Extended monthly as contributors submit novel categories.

## Failure modes

| Mode | Defense |
|---|---|
| Malicious contribution trying to weaponize the corpus | Reviewer gate; delayed publication for sensitive categories |
| Privacy leak in contributed trace | Anonymization validated at ingest; re-verified by reviewers |
| Corpus becomes stale | Monthly release cadence; contributor leaderboard incentivizes fresh submissions |
| Over-representation of one attack class | Balancing targets; reviewer re-weight by category |

## Metrics

- `lastraj.contributions_per_month`
- `lastraj.corpus_size_by_class`
- `lastraj.subscriber_count`
- `lastraj.monitor_evasion_rate_published` (quarterly)
- `lastraj.reviewer_throughput`
