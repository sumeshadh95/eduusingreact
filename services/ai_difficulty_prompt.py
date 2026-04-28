"""Prompt template for AI difficulty analysis."""


def difficulty_prompt(course: dict, material_text: str, summary: str) -> str:
    return f"""Analyze the difficulty of this short programme source course.

Course name: {course.get("course_name", "")}
Description: {course.get("description", "")}
Keywords: {", ".join(course.get("keywords", []))}
Material summary: {summary}
Material excerpt: {(material_text or "")[:3500]}

Classify the learner difficulty as exactly one of: Easy, Medium, Hard.

Use this rubric:
- Easy: beginner friendly, low prerequisite knowledge, mostly conceptual or guided practice
- Medium: some technical concepts, practice tasks, or tool use but still accessible with guidance
- Hard: advanced prerequisites, dense technical depth, independent complex projects, or specialist knowledge

Return ONLY valid JSON with this structure:
{{
  "level": "Easy | Medium | Hard",
  "rationale": "One concise sentence explaining why",
  "signals": ["Signal 1", "Signal 2", "Signal 3"]
}}"""
