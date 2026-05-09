"""Vertex-Eval skill-quality rubric tests."""
from __future__ import annotations

from harness_skills import Skill, SkillRecord, SourceKind, TrustTier
from vertex_eval.skills_rubric import (
    score_content_hash_present,
    score_provenance_present,
    score_skill_record,
    score_trust_tier_correct,
)


def _record(*, source_kind=SourceKind.DIALOGUE, source_id="s",
            tier=TrustTier.T2_AUTO_EXTRACTED, with_hash=True) -> SkillRecord:
    r = SkillRecord(
        skill=Skill(name="x", description="d", prompt="# Goal\nx"),
        source_kind=source_kind, source_id=source_id, trust_tier=tier,
    )
    return r.with_hash() if with_hash else r


def test_trust_tier_red_with_human_source_fails() -> None:
    r = _record(source_kind=SourceKind.HUMAN_AUTHORED, tier=TrustTier.RED_RETRACTED)
    assert not score_trust_tier_correct(r)


def test_provenance_check_requires_source_id() -> None:
    r = _record(source_id="")
    assert not score_provenance_present(r)


def test_content_hash_check() -> None:
    assert score_content_hash_present(_record())
    assert not score_content_hash_present(_record(with_hash=False))


def test_aggregate_score_high() -> None:
    assert score_skill_record(_record()) == 1.0


def test_aggregate_score_partial() -> None:
    s = score_skill_record(_record(with_hash=False))
    assert 0.0 <= s < 1.0
