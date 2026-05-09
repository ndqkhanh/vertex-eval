"""LaStraj red-team federation.

Tenants opt in to contribute anonymized adversarial trajectories. The
federation dedupes by content-hash, strips PII from step content, and exposes
a read-only query surface.
"""
from __future__ import annotations

import hashlib
import re
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import Trace


_PII_RX = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # email
    re.compile(r"\+?\d[\d\s().-]{7,}\d"),  # phone
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),  # card-like
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
]


def _scrub(text: str) -> str:
    for rx in _PII_RX:
        text = rx.sub("[REDACTED]", text or "")
    return text


def anonymize(trace: Trace) -> Trace:
    steps = [
        s.model_copy(
            update={
                "content": _scrub(s.content or ""),
                "tool_result": _scrub(s.tool_result or "") if s.tool_result else None,
            }
        )
        for s in trace.steps
    ]
    return trace.model_copy(update={"steps": steps, "tenant": "federated"})


def _hash(trace: Trace) -> str:
    parts = [trace.task_id]
    for s in trace.steps:
        parts.append(f"{s.role}|{s.tool_name}|{(s.content or '')[:256]}")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


@dataclass
class FederationEntry:
    digest: str
    trace: Trace
    contributors: int = 1


class LastrajFederation:
    def __init__(self) -> None:
        self._by_digest: Dict[str, FederationEntry] = {}
        self._lock = threading.Lock()

    def contribute(self, trace: Trace, anonymize_first: bool = True) -> FederationEntry:
        contributed = anonymize(trace) if anonymize_first else trace
        digest = _hash(contributed)
        with self._lock:
            entry = self._by_digest.get(digest)
            if entry is None:
                entry = FederationEntry(digest=digest, trace=contributed)
                self._by_digest[digest] = entry
            else:
                entry.contributors += 1
            return entry

    def get(self, digest: str) -> Optional[FederationEntry]:
        return self._by_digest.get(digest)

    def all(self) -> List[FederationEntry]:
        return list(self._by_digest.values())

    def __len__(self) -> int:
        return len(self._by_digest)
