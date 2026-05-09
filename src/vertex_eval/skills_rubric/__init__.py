"""Skill-quality rubric for Vertex-Eval."""
from __future__ import annotations

from harness_skills import SkillRecord, SourceKind, TrustTier


def score_trust_tier_correct(record: SkillRecord) -> bool:
    """Tier sanity-check — RED tiers must not be paired with HUMAN_AUTHORED source."""
    if record.trust_tier.is_red and record.source_kind is SourceKind.HUMAN_AUTHORED:
        return False
    if record.trust_tier is TrustTier.LEGACY and record.source_kind is not SourceKind.INJECTED:
        return record.source_kind is SourceKind.HUMAN_AUTHORED   # legacy from human seeds is fine
    return True


def score_provenance_present(record: SkillRecord) -> bool:
    return bool(record.source_id) and record.source_kind is not SourceKind.INJECTED


def score_content_hash_present(record: SkillRecord) -> bool:
    return bool(record.content_sha256) and len(record.content_sha256) == 64


def score_skill_record(record: SkillRecord) -> float:
    """Aggregate quality score in [0, 1]."""
    checks = [
        score_trust_tier_correct(record),
        score_provenance_present(record),
        score_content_hash_present(record),
    ]
    return sum(1 for c in checks if c) / len(checks)


__all__ = [
    "score_content_hash_present",
    "score_provenance_present",
    "score_skill_record",
    "score_trust_tier_correct",
]
