from race_engineer.voice.audio.models import AudioBuffer

MIN_AUDIO_DURATION_SECONDS = 0.1


def validate_audio(buffer: AudioBuffer) -> list[str]:
    """Return human-readable validation errors; empty list means valid."""
    errors: list[str] = []

    if not buffer.pcm_bytes:
        errors.append("audio buffer is empty")
        return errors

    if buffer.duration_seconds < MIN_AUDIO_DURATION_SECONDS:
        errors.append(
            f"audio too short: {buffer.duration_seconds:.3f}s "
            f"(minimum {MIN_AUDIO_DURATION_SECONDS}s)"
        )

    return errors
