"""Candidate skill matching."""

from services.talent_keywords import keywords


def matching_skills(candidate: dict, course: dict, trend: dict, programme: dict) -> list[str]:
    search_terms = keywords(course, trend, programme)
    return [skill for skill in candidate_skills(candidate) if skill_matches(skill, search_terms)]


def candidate_skills(candidate: dict) -> list[str]:
    return [skill.lower() for skill in candidate.get("skills", [])]


def skill_matches(skill: str, search_terms: set[str]) -> bool:
    skill_words = set(skill.replace("/", " ").replace("-", " ").split())
    return skill in search_terms or bool(skill_words.intersection(search_terms))
