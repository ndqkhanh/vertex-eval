"""Pydantic models for Vertex-Eval."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FailureClass(str, Enum):
    TASK_FAILURE = "task_failure"  # agent didn't achieve the goal
    SAFETY_VIOLATION = "safety_violation"  # policy / guardrail breach
    HALLUCINATION = "hallucination"  # unsupported factual claim
    TOOL_MISUSE = "tool_misuse"  # wrong tool / wrong args
    LOOP_OR_STUCK = "loop_or_stuck"  # repeated actions, no progress
    PROMPT_INJECTION = "prompt_injection"
    OTHER = "other"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TraceStep(BaseModel):
    index: int
    role: str  # "user" | "assistant" | "tool" | "system"
    content: str = ""
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[str] = None
    latency_ms: Optional[int] = None


class AuditEntry(BaseModel):
    index: int
    kind: str  # e.g. "file_write", "db_query", "auth_decision"
    ref: Optional[str] = None  # resource id
    outcome: str  # "allowed" | "denied" | "error"


class StateSnapshot(BaseModel):
    label: str  # "before" | "after" | intermediate tag
    fields: Dict[str, Any] = Field(default_factory=dict)


class Trace(BaseModel):
    trace_id: str
    tenant: str
    task_id: str
    steps: List[TraceStep] = Field(default_factory=list)
    audit: List[AuditEntry] = Field(default_factory=list)
    snapshots: List[StateSnapshot] = Field(default_factory=list)
    success: bool = True
    duration_ms: int = 0


class RubricItem(BaseModel):
    id: str
    description: str
    severity: Severity = Severity.MEDIUM
    # A python callable is resolved at registration time and kept off-schema.
    # We store a reference key here.
    check_key: str


class Rubric(BaseModel):
    id: str
    tenant: str
    version: int = 1
    items: List[RubricItem] = Field(default_factory=list)


class RubricResult(BaseModel):
    item_id: str
    passed: bool
    evidence: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    channels_agree: bool = True


class JudgeVote(BaseModel):
    judge: str  # "family:model-name"
    passed: bool
    reasoning: str = ""


class FailureAttribution(BaseModel):
    failure_class: FailureClass
    step_index: Optional[int] = None
    quote: str = ""
    severity: Severity = Severity.MEDIUM


class EvalReport(BaseModel):
    trace_id: str
    tenant: str
    rubric_id: str
    success: bool
    rubric_results: List[RubricResult]
    attributions: List[FailureAttribution] = Field(default_factory=list)
    judge_votes: List[JudgeVote] = Field(default_factory=list)
    cross_channel_confirmed: bool = False


class PasskSummary(BaseModel):
    k: int
    n_runs: int
    n_success: int
    pass_at_k: float
    pass_pow_k: float


class SLARule(BaseModel):
    suite: str
    k: int
    pass_pow_k_floor: float  # alert when Pass^k drops below this
