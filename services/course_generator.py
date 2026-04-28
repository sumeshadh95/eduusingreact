"""
course_generator.py — Generate the short programme from matched course data.

No streamlit imports.
"""


def generate_programme(course: dict, teacher: dict, weeks: int, ects: int) -> dict:
    """
    Generate a full programme dict from course, teacher, and analysis data.

    Args:
        course: the matched course dict
        teacher: the assigned teacher dict
        weeks: recommended duration in weeks
        ects: credit count

    Returns:
        dict with programme details including weekly structure
    """
    return {
        "title": "Game Development Winter Sprint",
        "based_on": course.get("course_name", ""),
        "ects": ects,
        "duration_weeks": weeks,
        "mode": "Online / Hybrid",
        "teacher": teacher.get("name", ""),
        "teacher_id": teacher.get("teacher_id", ""),
        "available_months": teacher.get("available_months", []),
        "target_students": (
            "Open to all Xamk students and external learners interested in "
            "game development, creative technology, and interactive media."
        ),
        "weekly_structure": {
            "Week 1": [
                "Introduction to Game Development — overview of the game industry, roles, and development pipeline",
                "Storytelling and Narrative Design — creating characters, worlds, and interactive plotlines",
                "Simple Programming Logic — variables, loops, conditionals, and event handling in game engines",
            ],
            "Week 2": [
                "Game Mechanics and Prototyping — designing core mechanics and building a playable prototype",
                "Testing and Feedback — playtesting with peers, collecting feedback, iterating on design",
                "Final Presentation — demonstrating the prototype and design document to the class",
            ],
        },
    }
