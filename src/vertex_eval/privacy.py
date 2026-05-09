"""Per-tenant isolation + PII redaction."""
from __future__ import annotations

import re
from typing import Any, Dict

_EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RX = re.compile(r"\+?\d[\d\s().-]{7,}\d")
_CARD_RX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
_SSN_RX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact(text: str) -> str:
    if not text:
        return text
    text = _EMAIL_RX.sub("[EMAIL]", text)
    # Card and SSN first — their digit runs would otherwise be swallowed by the
    # broader phone regex.
    text = _CARD_RX.sub("[CARD]", text)
    text = _SSN_RX.sub("[SSN]", text)
    text = _PHONE_RX.sub("[PHONE]", text)
    return text


def enforce_tenant(expected: str, trace_tenant: str) -> None:
    if expected != trace_tenant:
        raise PermissionError(f"tenant mismatch: expected {expected!r}, got {trace_tenant!r}")


def redact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, str):
            out[k] = redact(v)
        elif isinstance(v, dict):
            out[k] = redact_dict(v)
        else:
            out[k] = v
    return out
