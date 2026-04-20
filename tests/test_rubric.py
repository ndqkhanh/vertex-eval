import pytest

from vertex_eval.models import Rubric, RubricItem, Severity
from vertex_eval.rubric import RubricRegistry, default_rubric


def test_default_rubric_has_expected_items():
    r = default_rubric()
    ids = {i.id for i in r.items}
    assert {"task_succeeded", "no_prompt_injection", "no_destructive_unaudited", "state_mutation_expected"} <= ids


def test_registry_rejects_unknown_check_key():
    reg = RubricRegistry()
    bad = Rubric(id="bad", tenant="t", items=[RubricItem(id="x", description="", check_key="does_not_exist")])
    with pytest.raises(KeyError):
        reg.put(bad)


def test_check_happy_trace_passes(happy_trace):
    reg = RubricRegistry()
    rubric = default_rubric()
    reg.put(rubric)
    for item in rubric.items:
        result = reg.check_for(item)(happy_trace)
        assert result.passed, f"{item.id} should pass on happy_trace; evidence={result.evidence}"


def test_check_unaudited_destructive_fails(unaudited_destructive_trace):
    reg = RubricRegistry()
    rubric = default_rubric()
    reg.put(rubric)
    for item in rubric.items:
        if item.id == "no_destructive_unaudited":
            res = reg.check_for(item)(unaudited_destructive_trace)
            assert res.passed is False
            break
    else:
        raise AssertionError("expected rubric to contain no_destructive_unaudited")


def test_check_injection_fails(injection_trace):
    reg = RubricRegistry()
    rubric = default_rubric()
    reg.put(rubric)
    for item in rubric.items:
        if item.id == "no_prompt_injection":
            res = reg.check_for(item)(injection_trace)
            assert res.passed is False
            break


def test_extra_check_can_be_registered():
    reg = RubricRegistry()
    reg.register_check("always_pass", lambda t: __import__("vertex_eval.models", fromlist=["RubricResult"]).RubricResult(item_id="x", passed=True))
    rubric = Rubric(id="r", tenant="t", items=[RubricItem(id="x", description="", check_key="always_pass", severity=Severity.LOW)])
    reg.put(rubric)
    assert reg.get("r") is rubric
