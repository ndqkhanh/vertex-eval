"""Pass^k SLA alerts + pairwise decorrelation metric.

Per docs/53 (chaos-engineering next era), population-scale reliability depends
on failure *decorrelation* across agent instances — not just per-agent reliability.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence

from .models import SLARule
from .passk import pass_pow_k


@dataclass
class SLAAlert:
    suite: str
    k: int
    observed: float
    floor: float
    breach: bool


def check_rule(rule: SLARule, results: Sequence[bool]) -> SLAAlert:
    observed = pass_pow_k(results, rule.k)
    return SLAAlert(
        suite=rule.suite,
        k=rule.k,
        observed=observed,
        floor=rule.pass_pow_k_floor,
        breach=observed < rule.pass_pow_k_floor,
    )


def pairwise_decorrelation(runs_by_instance: Mapping[str, Sequence[bool]]) -> Dict[str, float]:
    """For each pair (A, B), compute 1 - P(both fail | A fails).

    Higher = more decorrelated (= better for population reliability).
    Returns a dict keyed by "A|B" for each pair (A < B alphabetically).
    """
    ids = sorted(runs_by_instance.keys())
    out: Dict[str, float] = {}
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            ra = list(runs_by_instance[a])
            rb = list(runs_by_instance[b])
            n = min(len(ra), len(rb))
            if n == 0:
                out[f"{a}|{b}"] = 1.0
                continue
            a_fail = sum(1 for k in range(n) if not ra[k])
            both_fail = sum(1 for k in range(n) if not ra[k] and not rb[k])
            if a_fail == 0:
                out[f"{a}|{b}"] = 1.0
            else:
                out[f"{a}|{b}"] = 1.0 - (both_fail / a_fail)
    return out
