from vertex_eval.attribution import attribute
from vertex_eval.models import FailureClass, RubricResult, Trace, TraceStep


def test_prompt_injection_attributed(injection_trace):
    results = [RubricResult(item_id="no_prompt_injection", passed=False)]
    out = attribute(injection_trace, results)
    classes = [a.failure_class for a in out]
    assert FailureClass.PROMPT_INJECTION in classes


def test_tool_misuse_attributed(unaudited_destructive_trace):
    results = [RubricResult(item_id="no_destructive_unaudited", passed=False)]
    out = attribute(unaudited_destructive_trace, results)
    classes = [a.failure_class for a in out]
    assert FailureClass.TOOL_MISUSE in classes


def test_loop_detected_even_without_rubric_failure():
    steps = [
        TraceStep(index=i, role="assistant", tool_name="Search", content="retry same thing")
        for i in range(5)
    ]
    trace = Trace(trace_id="t_loop", tenant="acme", task_id="loopy", steps=steps, success=False)
    out = attribute(trace, [RubricResult(item_id="task_succeeded", passed=False)])
    classes = [a.failure_class for a in out]
    assert FailureClass.LOOP_OR_STUCK in classes


def test_task_failure_added_when_no_other_attribution(happy_trace):
    # happy trace + claim task_succeeded failed — should emit TASK_FAILURE
    modified = happy_trace.model_copy(update={"success": False})
    out = attribute(modified, [RubricResult(item_id="task_succeeded", passed=False)])
    classes = [a.failure_class for a in out]
    assert FailureClass.TASK_FAILURE in classes


def test_no_false_attribution_when_everything_passes(happy_trace):
    out = attribute(happy_trace, [RubricResult(item_id="task_succeeded", passed=True)])
    # happy trace has no loops/injections/etc. → should yield no attributions
    assert out == []
