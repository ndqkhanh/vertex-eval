from vertex_eval.judges import JudgePool, latency_watchdog, strict_safety_judge
from vertex_eval.models import (
    AuditEntry,
    RubricItem,
    RubricResult,
    Severity,
    Trace,
)


def _item(id_="task_succeeded"):
    return RubricItem(id=id_, description=id_, severity=Severity.MEDIUM, check_key=id_)


def test_pool_returns_one_vote_per_judge(happy_trace):
    pool = JudgePool()
    votes = pool.vote(happy_trace, _item(), RubricResult(item_id="task_succeeded", passed=True))
    assert len(votes) == 3
    assert len({v.judge for v in votes}) == 3


def test_majority_pass():
    votes = [
        __import__("vertex_eval.models", fromlist=["JudgeVote"]).JudgeVote(judge="a", passed=True),
        __import__("vertex_eval.models", fromlist=["JudgeVote"]).JudgeVote(judge="b", passed=True),
        __import__("vertex_eval.models", fromlist=["JudgeVote"]).JudgeVote(judge="c", passed=False),
    ]
    assert JudgePool.majority(votes) is True


def test_majority_with_tie_is_false():
    votes = [
        __import__("vertex_eval.models", fromlist=["JudgeVote"]).JudgeVote(judge="a", passed=True),
        __import__("vertex_eval.models", fromlist=["JudgeVote"]).JudgeVote(judge="b", passed=False),
    ]
    assert JudgePool.majority(votes) is False


def test_strict_safety_fails_on_denied_audit():
    t = Trace(
        trace_id="t", tenant="acme", task_id="x",
        audit=[AuditEntry(index=0, kind="auth", ref="", outcome="denied")],
    )
    v = strict_safety_judge(t, _item("task_succeeded"), RubricResult(item_id="task_succeeded", passed=True))
    assert v.passed is False


def test_latency_watchdog_fails_over_30s():
    t = Trace(trace_id="t", tenant="acme", task_id="x", duration_ms=45_000)
    v = latency_watchdog(t, _item("task_succeeded"), RubricResult(item_id="task_succeeded", passed=True))
    assert v.passed is False


def test_latency_watchdog_ignores_non_latency_rubric():
    t = Trace(trace_id="t", tenant="acme", task_id="x", duration_ms=45_000)
    v = latency_watchdog(t, _item("no_prompt_injection"), RubricResult(item_id="no_prompt_injection", passed=True))
    assert v.passed is True
