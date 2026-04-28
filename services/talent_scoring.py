"""Candidate scoring for CoursePilot teacher recruitment."""

from services.talent_keywords import keywords
from services.talent_score_rules import candidate_score, match_reasons


def score_candidate(candidate: dict, course: dict, trend: dict, programme: dict) -> dict:
    skill_hits = matching_skills(candidate, course, trend, programme)
    signals = candidate_signals(candidate, programme)
    enriched = dict(candidate)
    enriched["match_score"] = candidate_score(skill_hits, signals)
    enriched["match_reasons"] = match_reasons(skill_hits, signals)
    return enriched


def matching_skills(candidate: dict, course: dict, trend: dict, programme: dict) -> list[str]:
    search_terms = keywords(course, trend, programme)
    return [skill for skill in candidate_skills(candidate) if skill_matches(skill, search_terms)]


def candidate_signals(candidate: dict, programme: dict) -> dict[str, bool]:
    return {
        "availability": has_availability_overlap(candidate, programme),
        "mode": supports_delivery_mode(candidate, programme),
        "teaching": has_teaching_background(candidate),
    }


def candidate_skills(candidate: dict) -> list[str]:
    return [skill.lower() for skill in candidate.get("skills", [])]


def skill_matches(skill: str, search_terms: set[str]) -> bool:
    skill_words = set(skill.replace("/", " ").replace("-", " ").split())
    return skill in search_terms or bool(skill_words.intersection(search_terms))


def has_availability_overlap(candidate: dict, programme: dict) -> bool:
    months = programme.get("available_months", [])
    return any(month in months for month in candidate.get("availability", []))


def supports_delivery_mode(candidate: dict, programme: dict) -> bool:
    return any(mode in programme.get("mode", "") for mode in candidate.get("teaching_modes", []))


def has_teaching_background(candidate: dict) -> bool:
    return any(
        "teach" in skill.lower() or "instructor" in skill.lower()
        for skill in candidate.get("skills", [])
    )
