import os
import anthropic
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

from backend.app.config import settings


claude_client = anthropic.Anthropic(
    api_key=settings.CLAUDE_API_KEY
)

openai_client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

groq_client = Groq(
    api_key=settings.GROQ_API_KEY
)


def call_claude(
    prompt: str,
    system_prompt: str | None = None
) -> str:

    response = claude_client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=1500,
        temperature=0,
        system=system_prompt if system_prompt else "",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.content[0].text.strip()



def call_openai(
    prompt: str,
    system_prompt: str | None = None
) -> str:

    response = openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt or ""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()



def call_groq(
    prompt: str,
    system_prompt: str | None = None
) -> str:

    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt or ""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()



def route_llm_call(
    provider: str,
    prompt: str,
    system_prompt: str | None = None
) -> str:

    provider = provider.lower()

    if provider == "claude":
        return call_claude(
            prompt,
            system_prompt
        )

    elif provider == "openai":
        return call_openai(
            prompt,
            system_prompt
        )

    elif provider == "groq":
        return call_groq(
            prompt,
            system_prompt
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )