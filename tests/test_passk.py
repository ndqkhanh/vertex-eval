import math

import pytest

from vertex_eval.passk import pass_at_k, pass_pow_k, summarise


def test_pass_at_k_all_success():
    assert pass_at_k(n=10, c=10, k=3) == 1.0


def test_pass_at_k_all_failure():
    assert pass_at_k(n=10, c=0, k=3) == 0.0


def test_pass_at_k_single_success_k1():
    # Pass@1 over 10 runs with 3 successes = 0.3
    assert math.isclose(pass_at_k(n=10, c=3, k=1), 0.3, rel_tol=1e-6)


def test_pass_at_k_k_exceeds_n_is_clamped():
    # k > n is clamped to n — so Pass@n with c>0 should be 1.0
    assert pass_at_k(n=5, c=1, k=10) == 1.0


def test_pass_at_k_invalid_args():
    with pytest.raises(ValueError):
        pass_at_k(n=0, c=0, k=1)
    with pytest.raises(ValueError):
        pass_at_k(n=3, c=5, k=1)
    with pytest.raises(ValueError):
        pass_at_k(n=3, c=0, k=0)


def test_pass_pow_k_all_true_is_one():
    assert pass_pow_k([True] * 10, k=3) == 1.0


def test_pass_pow_k_alternating_true_false():
    # Length-3 windows: every window spans both values → all fail.
    assert pass_pow_k([True, False, True, False, True, False, True, False], k=3) == 0.0


def test_pass_pow_k_short_history_falls_back_to_power():
    # fewer than k → (c/n)**k
    assert math.isclose(pass_pow_k([True, True], k=3), (2 / 2) ** 3, rel_tol=1e-6)
    assert math.isclose(pass_pow_k([True, False], k=3), (1 / 2) ** 3, rel_tol=1e-6)


def test_summarise_populates_all_fields():
    s = summarise([True, True, False, True], k=2)
    assert s.n_runs == 4
    assert s.n_success == 3
    assert 0 <= s.pass_at_k <= 1
    assert 0 <= s.pass_pow_k <= 1
