"""FastAPI surface for Vertex-Eval."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import ingest, passk, sla
from .engine import EvalEngine
from .lastraj import LastrajFederation
from .models import EvalReport, PasskSummary, SLARule, Trace
from .rubric import default_rubric


app = FastAPI(title="Vertex-Eval", version="0.1.0")
_store = ingest.TraceStore()
_engine = EvalEngine.default()
_federation = LastrajFederation()

# Seed with a default rubric for demo purposes
_engine.registry.put(default_rubric())


class IngestNativeRequest(BaseModel):
    payload: Dict[str, Any]


class IngestOtelRequest(BaseModel):
    payload: Dict[str, Any]


class EvaluateRequest(BaseModel):
    trace_id: str
    rubric_id: str = "default_v1"


class PasskRequest(BaseModel):
    results: List[bool]
    k: int = 3


class SLARequest(BaseModel):
    suite: str
    k: int
    pass_pow_k_floor: float
    results: List[bool]


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "service": "vertex-eval"}


@app.post("/v1/ingest/native")
def ingest_native(req: IngestNativeRequest) -> dict:
    try:
        trace = ingest.from_native(req.payload)
    except Exception as exc:  # pydantic validation error, etc.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _store.put(trace)
    return {"trace_id": trace.trace_id, "stored": True}


@app.post("/v1/ingest/otel")
def ingest_otel(req: IngestOtelRequest) -> dict:
    try:
        trace = ingest.from_otel(req.payload)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"missing field: {exc}") from exc
    _store.put(trace)
    return {"trace_id": trace.trace_id, "stored": True}


@app.post("/v1/evaluate", response_model=EvalReport)
def evaluate(req: EvaluateRequest) -> EvalReport:
    trace = _store.get(req.trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="trace not found")
    report = _engine.evaluate_by_id(trace, req.rubric_id)
    if report is None:
        raise HTTPException(status_code=404, detail="rubric not found")
    return report


@app.post("/v1/passk", response_model=PasskSummary)
def passk_summary(req: PasskRequest) -> PasskSummary:
    return passk.summarise(req.results, req.k)


@app.post("/v1/sla")
def sla_check(req: SLARequest) -> dict:
    rule = SLARule(suite=req.suite, k=req.k, pass_pow_k_floor=req.pass_pow_k_floor)
    alert = sla.check_rule(rule, req.results)
    return alert.__dict__


@app.post("/v1/lastraj/contribute")
def lastraj_contribute(trace: Trace) -> dict:
    entry = _federation.contribute(trace)
    return {"digest": entry.digest, "contributors": entry.contributors}


@app.get("/v1/lastraj/count")
def lastraj_count() -> dict:
    return {"count": len(_federation)}
