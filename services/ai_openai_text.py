"""OpenAI text-generation client."""

import logging

logger = logging.getLogger(__name__)


def generate_with_openai(
    system_prompt: str,
    user_prompt: str,
    *,
    api_key: str,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    import openai

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    logger.info("OpenAI generation completed successfully.")
    return response.choices[0].message.content.strip()
