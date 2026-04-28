"""AI recruitment outreach email generation."""

from services.ai_core import _generate_text


def generate_recruitment_email(
    candidate: dict,
    programme: dict,
    course: dict,
    api_key: str = None,
) -> tuple:
    email = _generate_text(
        "You are a careful university HR recruiter writing concise candidate outreach emails.",
        recruitment_prompt(candidate, programme, course),
        max_tokens=700,
        temperature=0.45,
        api_key=api_key,
    )
    if email:
        return (email, False)
    return (fallback_email(candidate, programme), True)


def recruitment_prompt(candidate: dict, programme: dict, course: dict) -> str:
    return f"""Write a warm, professional recruitment outreach email from Xamk Continuing Education to this candidate.

Candidate name: {candidate.get("name", "")}
Candidate headline: {candidate.get("headline", "")}
Candidate skills: {", ".join(candidate.get("skills", []))}
Candidate notes: {candidate.get("notes", "")}
Programme: {programme.get("title", "")}
Based on course: {course.get("course_name", "")}
Delivery mode: {programme.get("mode", "Online / Hybrid")}
Duration and credits: {programme.get("duration_weeks", "")} weeks, {programme.get("ects", "")} ECTS

Goal:
- Say Xamk is interested in going further with recruiting them and knowing them more.
- Ask for more details about their teaching availability and relevant experience.
- Explicitly ask them to send their latest CV and any additional recruitment documents, certificates, portfolio links, or teaching references that Xamk may use in the recruitment process.
- Mention that their background looks relevant to the programme.
- Keep the tone respectful, concise, and not pushy.
- Include a clear subject line.
- Do not omit the CV/documents request.

Return only the email text."""


def fallback_email(candidate: dict, programme: dict) -> str:
    return f"""Subject: Exploring teaching collaboration with Xamk

Dear {candidate.get("name", "Candidate")},

I hope you are doing well. We are exploring teachers for Xamk's {programme.get("title", "new short programme")}, and your background in {", ".join(candidate.get("skills", [])[:3])} looks highly relevant.

We would like to go further with recruiting you and learn more about your experience, teaching availability, and interest in contributing to this programme. Could you please share your latest CV and any additional documents or portfolio materials that Xamk may use as part of the recruitment process?

It would also be helpful to know your preferred teaching modes, available months, and examples of previous teaching, training, or project work related to this topic.

Best regards,
Xamk Continuing Education"""
