"""Candidate scoring for CoursePilot teacher recruitment."""


def keywords(course: dict, trend: dict, programme: dict) -> set:
    words = set()
    words.update(text_keywords(course.get("course_name", ""), min_length=3))
    words.update(text_keywords(trend.get("trend", ""), min_length=3))
    words.update(text_keywords(programme.get("title", ""), min_length=3))
    words.update(text_keywords(programme.get("target_students", ""), min_length=3))
    words.update(keyword.lower() for keyword in trend.get("keywords", []))
    for topic_list in programme.get("weekly_structure", {}).values():
        for topic in topic_list:
            words.update(text_keywords(topic, min_length=5))
    return words


def text_keywords(value: str, min_length: int) -> set[str]:
    tokens = value.replace("/", " ").replace("-", " ").split()
    return {
        token.strip(".,:;()[]").lower()
        for token in tokens
        if len(token.strip(".,:;()[]")) >= min_length
    }


def score_candidate(candidate: dict, course: dict, trend: dict, programme: dict) -> dict:
    skill_hits = matching_skills(candidate, course, trend, programme)
    availability_hit = has_availability_overlap(candidate, programme)
    mode_hit = supports_delivery_mode(candidate, programme)
    teaching_hit = has_teaching_background(candidate)
    score = candidate_score(skill_hits, availability_hit, mode_hit, teaching_hit)

    enriched = dict(candidate)
    enriched["match_score"] = score
    enriched["match_reasons"] = match_reasons(skill_hits, availability_hit, mode_hit, teaching_hit)
    return enriched


def matching_skills(candidate: dict, course: dict, trend: dict, programme: dict) -> list[str]:
    search_terms = keywords(course, trend, programme)
    hits = []
    for skill in [skill.lower() for skill in candidate.get("skills", [])]:
        skill_words = set(skill.replace("/", " ").replace("-", " ").split())
        if skill in search_terms or skill_words.intersection(search_terms):
            hits.append(skill)
    return hits


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


def candidate_score(skill_hits: list[str], availability_hit: bool, mode_hit: bool, teaching_hit: bool) -> int:
    score = 58 + min(len(skill_hits) * 8, 28)
    score += 7 if availability_hit else 0
    score += 4 if mode_hit else 0
    score += 3 if teaching_hit else 0
    return min(score, 98)


def match_reasons(
    skill_hits: list[str], availability_hit: bool, mode_hit: bool, teaching_hit: bool
) -> list[str]:
    reasons = []
    if skill_hits:
        reasons.append("skills match: " + ", ".join(sorted(set(skill_hits))[:4]))
    if availability_hit:
        reasons.append("available in programme months")
    if mode_hit:
        reasons.append("supports programme delivery mode")
    if teaching_hit:
        reasons.append("has teaching/instruction background")
    return reasons or ["general creative technology fit"]
