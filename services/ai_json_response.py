"""JSON parsing helpers for AI text responses."""

import json


def parse_json_response(raw: str) -> dict:
    if not raw:
        return {}
    return json.loads(strip_markdown_json(raw.strip()))


def strip_markdown_json(raw: str) -> str:
    if not raw.startswith("```"):
        return raw
    raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    return raw[4:].strip() if raw.startswith("json") else raw
