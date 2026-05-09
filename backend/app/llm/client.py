import anthropic

from openai import OpenAI

from groq import Groq

from backend.app.config import (
    settings
)

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

        "model":
            settings.CLAUDE_MODEL,

        "max_tokens":
            1500,

        "temperature":
            0,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    if system_prompt:

        request_params["system"] = (
            system_prompt
        )

    response = (
        claude_client.messages.create(
            **request_params
        )
    )

    return (
        response.content[0]
        .text
        .strip()
    )



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

    response = (
        openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,

            temperature=0,

            messages=messages
        )
    )

    return (
        response.choices[0]
        .message
        .content
        .strip()
    )



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

    response = (
        groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,

            temperature=0,

            messages=messages
        )
    )

    return (
        response.choices[0]
        .message
        .content
        .strip()
    )



def chat(
    prompt: str,
    system_prompt: str | None = None,
    provider: str | None = None
) -> str:
    """
    Universal enterprise LLM wrapper.

    Supports:
    - Claude
    - OpenAI
    - Groq
    """

    provider = validate_provider(
        provider or settings.LLM_PROVIDER
    )

    try:

        if provider == "claude":

            return call_claude(
                prompt=prompt,
                system_prompt=system_prompt
            )

        elif provider == "openai":

            return call_openai(
                prompt=prompt,
                system_prompt=system_prompt
            )

        elif provider == "groq":

            return call_groq(
                prompt=prompt,
                system_prompt=system_prompt
            )

        raise Exception(
            f"Unsupported provider: {provider}"
        )

    except Exception as e:

        raise Exception(
            f"{provider.upper()} API Error: {str(e)}"
        )



async def transcribe_with_openai(
    audio_file_path: str
) -> str:
    """
    OpenAI Whisper transcription.
    """

    with open(
        audio_file_path,
        "rb"
    ) as audio_file:

        transcript = (
            openai_client.audio.transcriptions.create(
                model=settings.OPENAI_WHISPER_MODEL,

                file=audio_file
            )
        )

    return transcript.text.strip()


async def transcribe_with_groq(
    audio_file_path: str
) -> str:
    """
    Groq Whisper transcription.
    """

    with open(
        audio_file_path,
        "rb"
    ) as audio_file:

        transcript = (
            groq_client.audio.transcriptions.create(
                model=settings.GROQ_WHISPER_MODEL,

                file=audio_file
            )
        )

    return transcript.text.strip()