"""Scoring rules for teacher-candidate matching."""


def candidate_score(skill_hits: list[str], signals: dict[str, bool]) -> int:
    score = 58 + min(len(skill_hits) * 8, 28)
    score += sum(SIGNAL_WEIGHTS[name] for name, active in signals.items() if active)
    return min(score, 98)


def match_reasons(skill_hits: list[str], signals: dict[str, bool]) -> list[str]:
    reasons = skill_reasons(skill_hits) + signal_reasons(signals)
    return reasons or ["general creative technology fit"]


def skill_reasons(skill_hits: list[str]) -> list[str]:
    return ["skills match: " + ", ".join(sorted(set(skill_hits))[:4])] if skill_hits else []


def signal_reasons(signals: dict[str, bool]) -> list[str]:
    return [SIGNAL_REASONS[name] for name, active in signals.items() if active]


SIGNAL_WEIGHTS = {
    "availability": 7,
    "mode": 4,
    "teaching": 3,
}

SIGNAL_REASONS = {
    "availability": "available in programme months",
    "mode": "supports programme delivery mode",
    "teaching": "has teaching/instruction background",
}
