"""HTTP request helper for LinkedIn Talent Solutions."""

import requests


def fetch_linkedin_elements(endpoint: str, headers: dict, query: str) -> tuple:
    try:
        response = requests.get(
            endpoint,
            headers=headers,
            params={"q": "search", "keywords": query},
            timeout=20,
        )
        response.raise_for_status()
        return (response.json().get("elements", []), "LinkedIn Talent Solutions connector returned results.")
    except Exception as exc:
        return ([], f"LinkedIn Talent Solutions search failed: {exc}")
