"""Candidate scoring for CoursePilot teacher recruitment."""

from services.talent_score_rules import candidate_score, match_reasons
from services.talent_signal_checks import candidate_signals
from services.talent_skill_matching import matching_skills


def score_candidate(candidate: dict, course: dict, trend: dict, programme: dict) -> dict:
    skill_hits = matching_skills(candidate, course, trend, programme)
    signals = candidate_signals(candidate, programme)
    enriched = dict(candidate)
    enriched["match_score"] = candidate_score(skill_hits, signals)
    enriched["match_reasons"] = match_reasons(skill_hits, signals)
    return enriched
