from vertex_eval.engine import EvalEngine
from vertex_eval.rubric import default_rubric


def test_engine_passes_happy_trace(happy_trace):
    e = EvalEngine.default()
    rubric = default_rubric()
    e.registry.put(rubric)
    report = e.evaluate(happy_trace, rubric)
    assert report.success is True
    assert report.cross_channel_confirmed is True
    assert not report.attributions


def test_engine_catches_injection(injection_trace):
    e = EvalEngine.default()
    rubric = default_rubric()
    e.registry.put(rubric)
    report = e.evaluate(injection_trace, rubric)
    assert report.success is False
    assert any(
        a.failure_class.value == "prompt_injection" for a in report.attributions
    )


def test_engine_flags_channels_disagree_on_unaudited_destructive(unaudited_destructive_trace):
    e = EvalEngine.default()
    rubric = default_rubric()
    e.registry.put(rubric)
    report = e.evaluate(unaudited_destructive_trace, rubric)
    assert report.success is False
    assert report.cross_channel_confirmed is False


def test_evaluate_by_id_lookup(happy_trace):
    e = EvalEngine.default()
    e.registry.put(default_rubric())
    got = e.evaluate_by_id(happy_trace, "default_v1")
    assert got is not None
    assert e.evaluate_by_id(happy_trace, "does_not_exist") is None
