"""
marketing.py — Static marketing copy for the generated programme.

All text is verbatim from the implementation brief.
"""


def get_marketing_content(programme: dict) -> dict:
    """
    Return marketing content for the programme.

    Args:
        programme: the generated programme dict

    Returns:
        dict with keys: website, social, email, tagline, selling_points
    """
    title = programme.get("title", "Game Development Winter Sprint")

    return {
        "website": (
            f"{title} — a 2-week, 3 ECTS online short programme by Xamk. "
            "Learn the fundamentals of game development: design, storytelling, "
            "programming logic, prototyping, and testing. Open to all students "
            "and professionals interested in creative technology and interactive "
            "media. No prior programming experience required. Earn credits while "
            "building your first game prototype. Available in November and January."
        ),
        "social": (
            f"🎮 Ready to build your first game? Join Xamk's {title} — "
            "a 2-week, 3 ECTS online programme covering game design, storytelling, "
            "programming, and prototyping. No experience needed! 🚀\n\n"
            "#GameDev #Xamk #ShortProgramme #LearnToCode #CreativeTech"
        ),
        "email": (
            f"Dear Partner,\n\n"
            f"We are pleased to announce Xamk's new short programme: {title}.\n\n"
            "This 2-week, 3 ECTS online programme introduces students to game "
            "development fundamentals — from design and storytelling to programming "
            "and prototyping. It is open to students from all fields, including those "
            "with no prior IT experience.\n\n"
            "We believe this programme would be an excellent opportunity for your "
            "students who are interested in creative technology, digital skills, "
            "or interdisciplinary learning.\n\n"
            "The programme runs in November 2026 and January 2027, with both online "
            "and hybrid options available.\n\n"
            "Please feel free to share this with your students and colleagues. "
            "We would be happy to discuss partnership opportunities.\n\n"
            "Best regards,\n"
            "Xamk Continuing Education"
        ),
        "tagline": "From trending topic to Xamk short programme — in weeks, not months.",
        "selling_points": [
            "Industry-relevant: Game development is one of the fastest-growing creative industries, and this programme gives students a practical foundation in just 2 weeks.",
            "Accessible to all: No prior programming or IT experience required — designed for students from any field, including nursing, business, and design.",
            "Credit-bearing and flexible: Earn 3 ECTS through a fully online or hybrid programme, with multiple intake windows (November, January, June).",
        ],
    }
