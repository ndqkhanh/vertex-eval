"""Pass@k and Pass^k metrics.

- ``Pass@k``: probability that at least one of the first k runs succeeds.
  Unbiased estimator per the HumanEval paper:
      Pass@k = 1 - C(n-c, k) / C(n, k)   when c <= n-k
  where n = total runs, c = successful runs.
- ``Pass^k``: probability that all k independently-sampled runs succeed
  simultaneously (stricter consistency metric). Empirically:
      Pass^k ≈ (c / n) ** k  under independence assumption, but we estimate
  it from observed consecutive-k windows when available.
"""
from __future__ import annotations

from math import comb
from typing import Sequence

from .models import PasskSummary


def pass_at_k(n: int, c: int, k: int) -> float:
    if k <= 0:
        raise ValueError("k must be >= 1")
    if n <= 0:
        raise ValueError("n must be >= 1")
    if c < 0 or c > n:
        raise ValueError("c must be in [0, n]")
    if k > n:
        k = n
    if c > n - k:
        return 1.0
    return 1.0 - (comb(n - c, k) / comb(n, k))


def pass_pow_k(results: Sequence[bool], k: int) -> float:
    """Empirical Pass^k over observed runs.

    Rolling window: fraction of length-k windows where every run succeeded.
    Falls back to (c/n)**k when fewer than k runs are present.
    """
    if k <= 0:
        raise ValueError("k must be >= 1")
    n = len(results)
    if n == 0:
        return 0.0
    if n < k:
        c = sum(results)
        p = c / n
        return p ** k
    windows = 0
    all_ok = 0
    for i in range(n - k + 1):
        windows += 1
        if all(results[i : i + k]):
            all_ok += 1
    return all_ok / windows if windows else 0.0


def summarise(results: Sequence[bool], k: int) -> PasskSummary:
    n = len(results)
    c = sum(results)
    return PasskSummary(
        k=k,
        n_runs=n,
        n_success=c,
        pass_at_k=pass_at_k(n, c, k) if n > 0 else 0.0,
        pass_pow_k=pass_pow_k(results, k),
    )
