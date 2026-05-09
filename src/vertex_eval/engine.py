"""Evaluation engine — orchestrates rubric check → evidence → judge pool → attribution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from . import attribution, evidence
from .judges import JudgePool
from .models import EvalReport, Rubric, RubricResult, Trace
from .rubric import RubricRegistry


@dataclass
class EvalEngine:
    registry: RubricRegistry
    judge_pool: JudgePool

    @classmethod
    def default(cls) -> "EvalEngine":
        return cls(registry=RubricRegistry(), judge_pool=JudgePool())

    def evaluate(self, trace: Trace, rubric: Rubric) -> EvalReport:
        rubric_results: list[RubricResult] = []
        judge_votes: list = []
        for item in rubric.items:
            check = self.registry.check_for(item)
            base = check(trace)
            confirmed = evidence.evaluate_agreement(trace, base)
            votes = self.judge_pool.vote(trace, item, confirmed)
            judge_votes.extend(votes)
            # Majority of judges overrides the base result
            majority_pass = JudgePool.majority(votes)
            merged = confirmed.model_copy(update={"passed": majority_pass and confirmed.passed})
            rubric_results.append(merged)

        attributions = attribution.attribute(trace, rubric_results)
        success = all(r.passed for r in rubric_results)
        cross_channel = evidence.report_confirmed(rubric_results)
        return EvalReport(
            trace_id=trace.trace_id,
            tenant=trace.tenant,
            rubric_id=rubric.id,
            success=success,
            rubric_results=rubric_results,
            attributions=attributions,
            judge_votes=judge_votes,
            cross_channel_confirmed=cross_channel,
        )

    def evaluate_by_id(self, trace: Trace, rubric_id: str) -> Optional[EvalReport]:
        rubric = self.registry.get(rubric_id)
        if rubric is None:
            return None
        return self.evaluate(trace, rubric)
