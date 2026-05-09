"""Trace ingestion.

Supports two shapes:
  * Native Vertex trace (already a :class:`Trace` shaped dict).
  * OTel-ish shape with `spans: [...]` — normalised into TraceStep objects.

Real adapters for LangSmith / Langfuse / Helicone would slot in here.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from .models import AuditEntry, StateSnapshot, Trace, TraceStep


def from_native(payload: Dict[str, Any]) -> Trace:
    return Trace(**payload)


def from_otel(payload: Dict[str, Any]) -> Trace:
    """Accepts a dict like {trace_id, tenant, task_id, spans:[...]}
    where each span has {name, attributes: {role, content, tool, ...}}.
    """
    steps: List[TraceStep] = []
    for i, span in enumerate(payload.get("spans", [])):
        attrs = span.get("attributes", {}) or {}
        role = attrs.get("role") or ("tool" if attrs.get("tool") else "assistant")
        steps.append(
            TraceStep(
                index=i,
                role=role,
                content=attrs.get("content", span.get("name", "")),
                tool_name=attrs.get("tool"),
                tool_args=attrs.get("tool_args"),
                tool_result=attrs.get("tool_result"),
                latency_ms=attrs.get("latency_ms"),
            )
        )
    audit = [AuditEntry(**a) for a in payload.get("audit", [])]
    snapshots = [StateSnapshot(**s) for s in payload.get("snapshots", [])]
    return Trace(
        trace_id=payload["trace_id"],
        tenant=payload["tenant"],
        task_id=payload["task_id"],
        steps=steps,
        audit=audit,
        snapshots=snapshots,
        success=bool(payload.get("success", True)),
        duration_ms=int(payload.get("duration_ms", 0)),
    )


class TraceStore:
    """In-memory, per-tenant store. Production: Postgres + object store."""

    def __init__(self) -> None:
        self._by_id: Dict[str, Trace] = {}
        self._by_tenant: Dict[str, List[str]] = {}
        self._lock = threading.Lock()

    def put(self, trace: Trace) -> None:
        with self._lock:
            self._by_id[trace.trace_id] = trace
            self._by_tenant.setdefault(trace.tenant, []).append(trace.trace_id)

    def get(self, trace_id: str) -> Optional[Trace]:
        return self._by_id.get(trace_id)

    def for_tenant(self, tenant: str) -> List[Trace]:
        ids = self._by_tenant.get(tenant, [])
        return [self._by_id[i] for i in ids if i in self._by_id]

    def __len__(self) -> int:
        return len(self._by_id)
