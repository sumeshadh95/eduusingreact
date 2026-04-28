"""
personalization.py — Personalized learning content.

Provides AI-generated personalization with hardcoded nursing fallbacks.
All fallback text is verbatim from the implementation brief.
"""

from services import ai_service


def get_personalized_chapters(course_name: str, student_field: str, api_key: str = None) -> tuple:
    """
    Get personalized chapters — tries AI first, falls back to hardcoded.

    Args:
        course_name: name of the course
        student_field: student's field of study
        api_key: optional AI provider API key

    Returns:
        tuple of (chapters: list, final_assignment: str, used_fallback: bool)
    """
    # Try AI generation
    data, used_fallback = ai_service.generate_personalized_chapters(
        course_name, student_field, api_key
    )

    if not used_fallback and data:
        chapters = data.get("chapters", [])
        final_assignment = data.get("final_assignment", _get_fallback_final_assignment())
        return (chapters, final_assignment, False)

    # Fallback to hardcoded nursing content
    return (_get_fallback_nursing_chapters(), _get_fallback_final_assignment(), True)


def _get_fallback_nursing_chapters() -> list:
    """Hardcoded nursing-personalized chapters (fallback)."""
    return [
        {
            "title": "Chapter 1 — Introduction to Game Development",
            "standard_explanation": (
                "An overview of how games are designed, built, tested, and "
                "presented. Students learn about the game industry, development "
                "roles, and the full production pipeline from concept to release."
            ),
            "personalized_explanation": (
                "In nursing, games can be used for training and simulation. "
                "For example, nursing students can practise emergency care, "
                "medicine administration, patient observation, and teamwork "
                "using a safe digital game before doing it in real life."
            ),
            "minigame": {
                "name": "Emergency Room Triage Game",
                "description": (
                    "The student sees 4 patients entering an emergency room "
                    "and chooses who needs urgent care first. Each patient has "
                    "visible symptoms and a brief medical history. The student "
                    "must prioritize based on severity to practise triage "
                    "decision-making."
                ),
            },
        },
        {
            "title": "Chapter 2 — Storytelling and Player Experience",
            "standard_explanation": (
                "How to create compelling narratives and design player "
                "experiences that keep users engaged. Covers character "
                "development, world-building, and interactive storytelling "
                "techniques."
            ),
            "personalized_explanation": (
                "In nursing, storytelling helps build empathy and understand "
                "patient journeys. A nurse who understands a patient's story — "
                "their fears, family situation, and daily challenges — provides "
                "better, more compassionate care. Games can simulate these "
                "patient narratives for training."
            ),
            "minigame": {
                "name": "Patient Journey Narrative",
                "description": (
                    "The student follows a virtual patient through a day in "
                    "hospital — from admission to discharge. At each stage, "
                    "the student makes care decisions and sees how their "
                    "choices affect the patient's comfort, recovery, and "
                    "emotional well-being."
                ),
            },
        },
        {
            "title": "Chapter 3 — Simple Programming Logic",
            "standard_explanation": (
                "Introduction to core programming concepts: variables, loops, "
                "conditionals, and event handling. Students learn how these "
                "building blocks power game behaviour and interactivity."
            ),
            "personalized_explanation": (
                "In nursing, logical thinking is essential for clinical "
                "decision-making. Nurses follow protocols and algorithms — "
                "for example, if a patient's blood pressure drops below X, "
                "then take action Y. Understanding programming logic helps "
                "nurses think systematically about medical decision trees."
            ),
            "minigame": {
                "name": "Medicine Dosage Calculator",
                "description": (
                    "The student receives a patient's weight, age, and "
                    "diagnosis, then uses simple if/then logic to calculate "
                    "the correct medicine dosage. Wrong answers trigger "
                    "feedback explaining the clinical reasoning behind the "
                    "correct dose."
                ),
            },
        },
        {
            "title": "Chapter 4 — Game Mechanics and Prototyping",
            "standard_explanation": (
                "Designing core game mechanics — scoring, resource management, "
                "physics, AI opponents — and building rapid prototypes to test "
                "whether ideas are fun before committing to full production."
            ),
            "personalized_explanation": (
                "In nursing, simulation and prototyping are used to design "
                "training exercises. A nursing simulation prototype might model "
                "vital-sign monitoring, where the student must respond to "
                "changing heart rate, oxygen levels, and blood pressure in "
                "real time — similar to a game mechanic."
            ),
            "minigame": {
                "name": "Vital Signs Monitor Prototype",
                "description": (
                    "The student watches a simulated patient monitor showing "
                    "heart rate, SpO₂, and blood pressure. Values change over "
                    "time, and the student must click the correct intervention "
                    "(oxygen mask, medication, call doctor) when readings go "
                    "outside safe ranges."
                ),
            },
        },
        {
            "title": "Chapter 5 — Testing and Feedback",
            "standard_explanation": (
                "How to playtest games with real users, collect structured "
                "feedback, and iterate on design. Covers usability testing, "
                "bug tracking, difficulty balancing, and analytics."
            ),
            "personalized_explanation": (
                "In nursing, peer feedback and clinical evaluation are central "
                "to professional growth. Nurses regularly participate in case "
                "reviews, simulation debriefs, and competency assessments. "
                "The testing mindset — observe, measure, improve — applies "
                "directly to clinical practice improvement."
            ),
            "minigame": {
                "name": "Clinical Feedback Simulator",
                "description": (
                    "The student watches a short video of a simulated nursing "
                    "procedure and must identify 3 things done well and 2 "
                    "areas for improvement. The game scores the student's "
                    "observation skills and compares their feedback to an "
                    "expert panel's assessment."
                ),
            },
        },
    ]


def _get_fallback_final_assignment() -> str:
    """Fallback final assignment text."""
    return (
        "Final Assignment: Design a Game Concept for Nursing Education\n\n"
        "Design a simple game concept that could be used to train nursing "
        "students in one specific clinical skill (e.g., wound care, patient "
        "communication, medication safety). Your submission should include:\n\n"
        "• A one-page game design document describing the concept, target "
        "audience, core mechanic, and learning objective.\n"
        "• A paper or digital prototype (wireframe, storyboard, or simple "
        "playable demo).\n"
        "• A short reflection (300 words) on how game-based learning could "
        "improve nursing education.\n\n"
        "This assignment bridges game development skills with real-world "
        "nursing training needs."
    )


# Keep legacy functions for backward compatibility
def get_nursing_chapters() -> list:
    return _get_fallback_nursing_chapters()


def get_final_assignment() -> str:
    return _get_fallback_final_assignment()
