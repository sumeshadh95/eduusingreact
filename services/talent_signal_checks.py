"""Boolean candidate signals for talent scoring."""


def candidate_signals(candidate: dict, programme: dict) -> dict[str, bool]:
    return {
        "availability": has_availability_overlap(candidate, programme),
        "mode": supports_delivery_mode(candidate, programme),
        "teaching": has_teaching_background(candidate),
    }


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
