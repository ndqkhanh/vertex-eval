"""Vertex-Eval MCP server stub.

Tools published:

- ``vertex.score(trace_id, channels)`` — aggregated score from the judge pool.
- ``vertex.pass_at_k(samples)`` — Pass@k.
- ``vertex.pass_power_k(samples)`` — Pass^k.
- ``vertex.anonymize(text)`` — PII-stripped text.
- ``vertex.health()`` — adapter health.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any


_PII_PATTERNS = (
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<EMAIL>"),
    (re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"), "<PHONE>"),
    (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), "<CC>"),
)


def _stub_pass_at_k(samples: list[bool]) -> float:
    if not samples:
        return 0.0
    return 1.0 if any(samples) else 0.0


def _stub_pass_power_k(samples: list[bool]) -> float:
    if not samples:
        return 0.0
    return 1.0 if all(samples) else 0.0


def _stub_anonymize(text: str) -> str:
    out = text
    for pat, repl in _PII_PATTERNS:
        out = pat.sub(repl, out)
    return out


def main() -> int:
    line = sys.stdin.readline()
    if not line.strip():
        print(json.dumps({"error": "no input"}))
        return 0
    req = json.loads(line)
    tool = req.get("tool", "vertex.health")
    args = req.get("args") or {}
    if tool == "vertex.score":
        # Stub returns 0.85 — production wires the real judge pool.
        print(json.dumps({"tool": tool, "result": {"score": 0.85, "judges": 3}}))
    elif tool == "vertex.pass_at_k":
        out = _stub_pass_at_k(args.get("samples") or [])
        print(json.dumps({"tool": tool, "result": {"pass_at_k": out}}))
    elif tool == "vertex.pass_power_k":
        out = _stub_pass_power_k(args.get("samples") or [])
        print(json.dumps({"tool": tool, "result": {"pass_power_k": out}}))
    elif tool == "vertex.anonymize":
        out = _stub_anonymize(args.get("text", ""))
        print(json.dumps({"tool": tool, "result": {"text": out}}))
    elif tool == "vertex.health":
        print(json.dumps({"tool": tool, "result": {"ok": True}}))
    else:
        print(json.dumps({"tool": tool, "error": f"unknown tool {tool}"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
