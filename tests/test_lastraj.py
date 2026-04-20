from vertex_eval.lastraj import LastrajFederation, anonymize
from vertex_eval.models import Trace, TraceStep


def _trace_with_pii():
    return Trace(
        trace_id="t1",
        tenant="acme",
        task_id="secret_leak",
        steps=[
            TraceStep(index=0, role="user", content="call me at 555-123-4567 or bob@example.com"),
            TraceStep(index=1, role="assistant", content="got it bob@example.com"),
        ],
    )


def test_anonymize_strips_email_and_phone():
    t = anonymize(_trace_with_pii())
    for s in t.steps:
        assert "bob@example.com" not in (s.content or "")
        assert "555-123-4567" not in (s.content or "")
    assert t.tenant == "federated"


def test_contribute_dedupes_by_digest():
    f = LastrajFederation()
    a = f.contribute(_trace_with_pii())
    b = f.contribute(_trace_with_pii())
    assert a.digest == b.digest
    assert b.contributors == 2
    assert len(f) == 1


def test_different_traces_produce_different_digests():
    f = LastrajFederation()
    t1 = _trace_with_pii()
    t2 = _trace_with_pii().model_copy(update={"task_id": "different_task"})
    a = f.contribute(t1)
    b = f.contribute(t2)
    assert a.digest != b.digest
    assert len(f) == 2


def test_contribute_without_anonymize_keeps_tenant():
    f = LastrajFederation()
    entry = f.contribute(_trace_with_pii(), anonymize_first=False)
    assert entry.trace.tenant == "acme"
