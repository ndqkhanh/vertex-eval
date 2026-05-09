from vertex_eval.ingest import TraceStore, from_native, from_otel


def test_from_native_round_trips(happy_trace):
    payload = happy_trace.model_dump()
    t = from_native(payload)
    assert t.trace_id == happy_trace.trace_id
    assert len(t.steps) == len(happy_trace.steps)


def test_from_otel_normalises_spans_into_steps():
    payload = {
        "trace_id": "t_otel",
        "tenant": "acme",
        "task_id": "otel_demo",
        "spans": [
            {"name": "user_message", "attributes": {"role": "user", "content": "hi"}},
            {"name": "agent", "attributes": {"role": "assistant", "content": "hello"}},
            {"name": "tool", "attributes": {"tool": "Read", "content": "", "tool_args": {"path": "/f"}}},
        ],
    }
    t = from_otel(payload)
    assert t.trace_id == "t_otel"
    assert [s.role for s in t.steps] == ["user", "assistant", "tool"]
    assert t.steps[2].tool_name == "Read"


def test_otel_requires_trace_id():
    import pytest

    with pytest.raises(KeyError):
        from_otel({"tenant": "acme", "task_id": "x", "spans": []})


def test_trace_store_puts_and_gets(happy_trace):
    s = TraceStore()
    s.put(happy_trace)
    assert s.get(happy_trace.trace_id) is happy_trace
    assert happy_trace.trace_id in [t.trace_id for t in s.for_tenant("acme")]


def test_trace_store_tenant_isolation(happy_trace):
    s = TraceStore()
    s.put(happy_trace)
    assert s.for_tenant("other") == []
