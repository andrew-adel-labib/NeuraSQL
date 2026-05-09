import io
import wave
import audioop


def pcm_to_wav(
    pcm_data: bytes,
    channels: int = 1,
    sample_width: int = 2,
    sample_rate: int = 16000
) -> bytes:
    """
    Convert raw PCM audio to WAV format.
    """

    wav_buffer = io.BytesIO()

    with wave.open(
        wav_buffer,
        "wb"
    ) as wav_file:

        wav_file.setnchannels(
            channels
        )

        wav_file.setsampwidth(
            sample_width
        )

        wav_file.setframerate(
            sample_rate
        )

        wav_file.writeframes(
            pcm_data
        )

    wav_buffer.seek(0)

    return wav_buffer.read()


def normalize_audio(
    audio_bytes: bytes,
    sample_width: int = 2
) -> bytes:
    """
    Normalize audio volume.
    """

    try:

        max_volume = audioop.max(
            audio_bytes,
            sample_width
        )

        if max_volume == 0:

            return audio_bytes

        target_volume = 30000

        factor = (
            target_volume / max_volume
        )

        normalized_audio = (
            audioop.mul(
                audio_bytes,
                sample_width,
                factor
            )
        )

        return normalized_audio

    except Exception:

        return audio_bytes


def validate_audio(
    audio_bytes: bytes
) -> bool:
    """
    Basic audio validation.
    """

    if not audio_bytes:

        return False

    if len(audio_bytes) < 100:

        return False

    return True


def prepare_audio(
    pcm_audio: bytes
) -> bytes:
    """
    Full preprocessing pipeline.

    PCM
    → normalize
    → wav conversion
    """

    normalized = normalize_audio(
        pcm_audio
    )

    wav_audio = pcm_to_wav(
        normalized
    )

    return wav_audio