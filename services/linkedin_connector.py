"""Placeholder LinkedIn Talent Solutions connector."""

import os

import requests


class LinkedInTalentConnector:
    """
    Placeholder for approved LinkedIn Talent Solutions / RSC integrations.

    Required production env vars:
    - LINKEDIN_RSC_ACCESS_TOKEN
    - LINKEDIN_VERSION, default 202603
    - LINKEDIN_RSC_SEARCH_ENDPOINT, an approved customer/partner endpoint
    """

    def __init__(self):
        self.token = os.environ.get("LINKEDIN_RSC_ACCESS_TOKEN", "").strip()
        self.version = os.environ.get("LINKEDIN_VERSION", "202603").strip()
        self.endpoint = os.environ.get("LINKEDIN_RSC_SEARCH_ENDPOINT", "").strip()

    @property
    def configured(self) -> bool:
        return bool(self.token and self.endpoint)

    def search(self, query: str) -> tuple:
        if not self.configured:
            return (
                [],
                "LinkedIn partner credentials are not configured. Showing Xamk demo talent-pool matches.",
            )
        return self.fetch_results(query)

    def fetch_results(self, query: str) -> tuple:
        try:
            response = requests.get(
                self.endpoint,
                headers=self.headers(),
                params={"q": "search", "keywords": query},
                timeout=20,
            )
            response.raise_for_status()
            return (response.json().get("elements", []), "LinkedIn Talent Solutions connector returned results.")
        except Exception as exc:
            return ([], f"LinkedIn Talent Solutions search failed: {exc}")

    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "LinkedIn-Version": self.version,
            "X-Restli-Protocol-Version": "2.0.0",
        }
