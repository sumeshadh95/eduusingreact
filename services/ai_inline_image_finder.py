"""Find inline image data in Gemini responses."""


def first_inline_image(data: dict) -> dict | None:
    for candidate in candidate_list(data):
        inline = candidate_inline_image(candidate)
        if inline:
            return inline
    return None


def candidate_inline_image(candidate: dict) -> dict | None:
    for part in part_list(candidate):
        inline = inline_data(part)
        if inline.get("data"):
            return inline
    return None


def candidate_list(data: dict) -> list[dict]:
    return data.get("candidates") if data.get("candidates") is not None else []


def part_list(candidate: dict) -> list[dict]:
    content = candidate.get("content") if candidate.get("content") is not None else {}
    return content.get("parts") if content.get("parts") is not None else []


def inline_data(part: dict) -> dict:
    inline = part.get("inlineData")
    return inline if inline is not None else part.get("inline_data", {})
