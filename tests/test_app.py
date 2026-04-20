from fastapi.testclient import TestClient

from vertex_eval.app import app


client = TestClient(app)


def _payload():
    return {
        "trace_id": "http_t1",
        "tenant": "acme",
        "task_id": "via_http",
        "steps": [
            {"index": 0, "role": "user", "content": "write config"},
            {
                "index": 1,
                "role": "tool",
                "tool_name": "Write",
                "tool_args": {"path": "/workspace/config.json"},
                "tool_result": "ok",
            },
        ],
        "audit": [{"index": 0, "kind": "file_write", "ref": "/workspace/config.json", "outcome": "allowed"}],
        "snapshots": [
            {"label": "before", "fields": {"config.json": None}},
            {"label": "after", "fields": {"config.json": "{}"}},
        ],
        "success": True,
        "duration_ms": 800,
    }


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_ingest_then_evaluate_round_trip():
    r = client.post("/v1/ingest/native", json={"payload": _payload()})
    assert r.status_code == 200
    trace_id = r.json()["trace_id"]
    r2 = client.post("/v1/evaluate", json={"trace_id": trace_id, "rubric_id": "default_v1"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["success"] is True
    assert body["cross_channel_confirmed"] is True


def test_evaluate_unknown_trace_404s():
    r = client.post("/v1/evaluate", json={"trace_id": "does_not_exist", "rubric_id": "default_v1"})
    assert r.status_code == 404


def test_passk_endpoint():
    r = client.post("/v1/passk", json={"results": [True, True, False, True], "k": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["k"] == 2
    assert 0.0 <= body["pass_at_k"] <= 1.0


def test_sla_endpoint_flags_breach():
    r = client.post(
        "/v1/sla",
        json={"suite": "coding", "k": 3, "pass_pow_k_floor": 0.99, "results": [True, False, True, True]},
    )
    assert r.status_code == 200
    assert r.json()["breach"] is True


def test_lastraj_contribute_dedupes():
    t = {
        "trace_id": "lst_t1",
        "tenant": "acme",
        "task_id": "red",
        "steps": [{"index": 0, "role": "user", "content": "email me at bob@example.com"}],
    }
    a = client.post("/v1/lastraj/contribute", json=t).json()
    b = client.post("/v1/lastraj/contribute", json=t).json()
    assert a["digest"] == b["digest"]
    assert b["contributors"] >= 2
    count = client.get("/v1/lastraj/count").json()["count"]
    assert count >= 1


def test_otel_ingest():
    r = client.post(
        "/v1/ingest/otel",
        json={
            "payload": {
                "trace_id": "otel_http",
                "tenant": "acme",
                "task_id": "otel_task",
                "spans": [
                    {"name": "u", "attributes": {"role": "user", "content": "hi"}},
                    {"name": "a", "attributes": {"role": "assistant", "content": "done"}},
                ],
            }
        },
    )
    assert r.status_code == 200
    assert r.json()["trace_id"] == "otel_http"
