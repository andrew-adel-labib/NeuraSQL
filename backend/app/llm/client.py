import anthropic
from openai import OpenAI
from groq import Groq

from backend.app.config import settings
from backend.app.llm.model_registry import (
    validate_provider
)



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
    request_params = {
        "model": settings.CLAUDE_MODEL,
        "max_tokens": 1500,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    if system_prompt:
        request_params["system"] = system_prompt

    response = claude_client.messages.create(
        **request_params
    )

    return response.content[0].text.strip()



def call_openai(
    prompt: str,
    system_prompt: str | None = None
) -> str:

    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    response = openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=0,
        messages=messages
    )

    return response.choices[0].message.content.strip()



def call_groq(
    prompt: str,
    system_prompt: str | None = None
) -> str:

    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=0,
        messages=messages
    )

    return response.choices[0].message.content.strip()



def chat(
    prompt: str,
    system_prompt: str | None = None,
    provider: str | None = None
) -> str:
    """
    Universal enterprise LLM wrapper supporting:
    - Claude
    - OpenAI GPT
    - Groq
    """

    provider = validate_provider(
        provider or settings.LLM_PROVIDER
    )

    try:

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
            raise Exception(
                f"Unsupported provider: {provider}"
            )

    except Exception as e:
        raise Exception(
            f"{provider.upper()} API Error: {str(e)}"
        )