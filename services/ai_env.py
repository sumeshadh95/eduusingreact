"""Environment and AI model-name helpers."""

import os


def env(name: str) -> str:
    return os.environ.get(name, "").strip()


def normalize_model_name(model: str) -> str:
    candidate = (model or "").strip()
    return candidate.split("/", 1)[1] if candidate.startswith("models/") else candidate


def unique_model_candidates(candidates: list[str]) -> list[str]:
    unique = []
    for candidate in map(normalize_model_name, candidates):
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique
