import tempfile

from openai import OpenAI

from backend.app.config import (
    settings
)


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


async def transcribe_audio(
    audio_bytes: bytes
) -> str:
    """
    OpenAI Whisper transcription.
    """

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_audio:

            temp_audio.write(
                audio_bytes
            )

            temp_audio.flush()

            with open(
                temp_audio.name,
                "rb"
            ) as audio_file:

                transcript = (
                    client.audio.transcriptions.create(
                        model="whisper-1",

                        file=audio_file
                    )
                )

            return transcript.text.strip()

    except Exception as e:

        raise Exception(
            f"Speech transcription failed: {str(e)}"
        )