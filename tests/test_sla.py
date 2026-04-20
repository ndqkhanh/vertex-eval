from vertex_eval.models import SLARule
from vertex_eval.sla import check_rule, pairwise_decorrelation


def test_sla_breach_when_observed_below_floor():
    rule = SLARule(suite="coding", k=3, pass_pow_k_floor=0.9)
    results = [True, True, False, True, True, False]
    alert = check_rule(rule, results)
    assert alert.breach is True
    assert alert.observed < alert.floor


def test_sla_not_breached_when_consistent():
    rule = SLARule(suite="coding", k=3, pass_pow_k_floor=0.5)
    results = [True, True, True, True, True, True]
    alert = check_rule(rule, results)
    assert alert.breach is False
    assert alert.observed == 1.0


def test_pairwise_decorrelation_identical_agents_is_zero():
    runs = {
        "a": [True, False, True, False],
        "b": [True, False, True, False],  # same pattern
    }
    out = pairwise_decorrelation(runs)
    assert out["a|b"] == 0.0  # perfectly correlated failures


def test_pairwise_decorrelation_orthogonal_agents_is_one():
    runs = {
        "a": [True, False, True, False],
        "b": [False, True, False, True],  # a fails where b succeeds
    }
    out = pairwise_decorrelation(runs)
    assert out["a|b"] == 1.0


def test_pairwise_decorrelation_with_no_failures_is_one():
    runs = {"a": [True, True], "b": [False, False]}
    out = pairwise_decorrelation(runs)
    assert out["a|b"] == 1.0  # a never fails → no co-failure possible
