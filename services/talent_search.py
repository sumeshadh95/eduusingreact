"""Teacher recruitment talent matching facade."""

from services.linkedin_connector import LinkedInTalentConnector
from services.talent_pool import load_talent_pool
from services.talent_scoring import score_candidate


def search_probable_teachers(course: dict, trend: dict, programme: dict, limit: int = 5) -> tuple:
    connector = LinkedInTalentConnector()
    linkedin_results, status = connector.search(search_query(course, trend, programme))
    combined = load_talent_pool() + linkedin_results
    scored = [score_candidate(candidate, course, trend, programme) for candidate in combined]
    scored.sort(key=lambda item: item.get("match_score", 0), reverse=True)
    return (scored[:limit], status)


def search_query(course: dict, trend: dict, programme: dict) -> str:
    return " ".join(
        [
            course.get("course_name", ""),
            trend.get("trend", ""),
            " ".join(trend.get("keywords", [])),
            programme.get("title", ""),
        ]
    ).strip()
