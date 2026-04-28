"""Keyword extraction for teacher-candidate scoring."""


def keywords(course: dict, trend: dict, programme: dict) -> set[str]:
    words = set()
    for value in source_text_values(course, trend, programme):
        words.update(text_keywords(value, min_length=3))
    words.update(keyword.lower() for keyword in trend.get("keywords", []))
    words.update(weekly_structure_keywords(programme))
    return words


def source_text_values(course: dict, trend: dict, programme: dict) -> list[str]:
    return [
        course.get("course_name", ""),
        trend.get("trend", ""),
        programme.get("title", ""),
        programme.get("target_students", ""),
    ]


def weekly_structure_keywords(programme: dict) -> set[str]:
    return {
        keyword
        for topic_list in programme.get("weekly_structure", {}).values()
        for topic in topic_list
        for keyword in text_keywords(topic, min_length=5)
    }


def text_keywords(value: str, min_length: int) -> set[str]:
    return {
        normalized
        for token in value.replace("/", " ").replace("-", " ").split()
        if len(normalized := token.strip(".,:;()[]").lower()) >= min_length
    }
