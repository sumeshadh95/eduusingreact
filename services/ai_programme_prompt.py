"""Programme-generation prompt template."""


def programme_prompt(
    course: dict,
    teacher: dict,
    trend: dict,
    weeks: int,
    ects: int,
    summary: str,
    approach: str = None,
) -> str:
    teacher_name = teacher.get("name", "")
    course_name = course.get("course_name", "")
    return f"""Create a demo-ready university short programme plan.

Matched course: {course_name}
Trend: {trend.get("trend", "")}
Trend keywords: {", ".join(trend.get("keywords", []))}
Recommended duration: {weeks} weeks
Credits: {ects} ECTS
Teacher: {teacher_name}
Available months: {", ".join(teacher.get("available_months", []))}
Course material summary: {summary}
{approach_instruction(approach)}

Return ONLY valid JSON with this exact structure:
{{
  "title": "A concise, marketable programme title",
  "based_on": "{course_name}",
  "ects": {ects},
  "duration_weeks": {weeks},
  "mode": "Online / Hybrid",
  "teacher": "{teacher_name}",
  "teacher_id": "{teacher.get("teacher_id", "")}",
  "available_months": ["month names copied from the teacher availability"],
  "target_students": "Specific target learner group in 1-2 sentences",
  "learning_outcomes": ["Outcome 1", "Outcome 2", "Outcome 3"],
  "weekly_structure": {{"Week 1": ["Topic title - concrete activity students do"]}},
  "assessment": "Short description of how students complete the 3 ECTS work",
  "demo_pitch": "One persuasive sentence explaining why this programme should run now"
}}

Make the programme feel current, practical, and credible for Xamk continuing education. Create exactly {weeks} week entries."""


def approach_instruction(approach: str = None) -> str:
    if not approach:
        return ""
    return (
        f"\nAlternative approach requested: {approach}. Make the whole programme structure, "
        "framing, title, outcomes, weekly activities, and assessment reflect this approach "
        "while staying credible for Xamk."
    )
