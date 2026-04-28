"""Small HTTP response helpers shared by AI clients."""


def response_json(response) -> dict:
    try:
        return response.json()
    except ValueError:
        return {}
