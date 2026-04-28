"""
talent_search.py - Teacher recruitment talent-pool matching.

The official LinkedIn Talent Solutions / RSC APIs are partner-gated. This
module keeps the demo working with local recruitment-pool data and exposes a
small connector shape for future approved LinkedIn credentials.
"""

import json
import os
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_talent_pool() -> list:
    path = DATA_DIR / "talent_pool.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _keywords(course: dict, trend: dict, programme: dict) -> set:
    words = set()
    for value in [
        course.get("course_name", ""),
        trend.get("trend", ""),
        programme.get("title", ""),
        programme.get("target_students", ""),
    ]:
        for token in value.replace("/", " ").replace("-", " ").split():
            token = token.strip(".,:;()[]").lower()
            if len(token) > 2:
                words.add(token)
    for keyword in trend.get("keywords", []):
        words.add(keyword.lower())
    for topic_list in programme.get("weekly_structure", {}).values():
        for topic in topic_list:
            for token in topic.replace("/", " ").replace("-", " ").split():
                token = token.strip(".,:;()[]").lower()
                if len(token) > 4:
                    words.add(token)
    return words


def _score_candidate(candidate: dict, course: dict, trend: dict, programme: dict) -> dict:
    keywords = _keywords(course, trend, programme)
    skills = [skill.lower() for skill in candidate.get("skills", [])]
    skill_hits = []
    for skill in skills:
        skill_words = set(skill.replace("/", " ").replace("-", " ").split())
        if skill in keywords or skill_words.intersection(keywords):
            skill_hits.append(skill)

    availability = candidate.get("availability", [])
    availability_hit = any(month in programme.get("available_months", []) for month in availability)
    mode_hit = any(mode in programme.get("mode", "") for mode in candidate.get("teaching_modes", []))
    teaching_hit = any("teach" in skill or "instructor" in skill for skill in skills)

    score = 58 + min(len(skill_hits) * 8, 28)
    if availability_hit:
        score += 7
    if mode_hit:
        score += 4
    if teaching_hit:
        score += 3
    score = min(score, 98)

    reasons = []
    if skill_hits:
        reasons.append("skills match: " + ", ".join(sorted(set(skill_hits))[:4]))
    if availability_hit:
        reasons.append("available in programme months")
    if mode_hit:
        reasons.append("supports programme delivery mode")
    if teaching_hit:
        reasons.append("has teaching/instruction background")
    if not reasons:
        reasons.append("general creative technology fit")

    enriched = dict(candidate)
    enriched["match_score"] = score
    enriched["match_reasons"] = reasons
    return enriched


class LinkedInTalentConnector:
    """
    Placeholder for approved LinkedIn Talent Solutions / RSC integrations.

    Required production env vars:
    - LINKEDIN_RSC_ACCESS_TOKEN
    - LINKEDIN_VERSION, default 202603
    - LINKEDIN_RSC_SEARCH_ENDPOINT, an approved customer/partner endpoint
    """

    def __init__(self):
        self.token = os.environ.get("LINKEDIN_RSC_ACCESS_TOKEN", "").strip()
        self.version = os.environ.get("LINKEDIN_VERSION", "202603").strip()
        self.endpoint = os.environ.get("LINKEDIN_RSC_SEARCH_ENDPOINT", "").strip()

    @property
    def configured(self) -> bool:
        return bool(self.token and self.endpoint)

    def search(self, query: str) -> tuple:
        if not self.configured:
            return (
                [],
                "LinkedIn partner credentials are not configured. Showing Xamk demo talent-pool matches.",
            )

        try:
            response = requests.get(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "LinkedIn-Version": self.version,
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                params={"q": "search", "keywords": query},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            return ([], f"LinkedIn Talent Solutions search failed: {exc}")

        return (data.get("elements", []), "LinkedIn Talent Solutions connector returned results.")


def search_probable_teachers(course: dict, trend: dict, programme: dict, limit: int = 5) -> tuple:
    query = " ".join(
        [
            course.get("course_name", ""),
            trend.get("trend", ""),
            " ".join(trend.get("keywords", [])),
            programme.get("title", ""),
        ]
    ).strip()

    connector = LinkedInTalentConnector()
    linkedin_results, status = connector.search(query)

    local_candidates = load_talent_pool()
    combined = local_candidates + linkedin_results
    scored = [
        _score_candidate(candidate, course, trend, programme)
        for candidate in combined
    ]
    scored.sort(key=lambda item: item.get("match_score", 0), reverse=True)
    return (scored[:limit], status)
