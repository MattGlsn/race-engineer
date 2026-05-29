import io
import wave

from race_engineer.voice.audio.models import AudioBuffer


def audio_buffer_to_wav(buffer: AudioBuffer) -> bytes:
    """Encode captured PCM audio as WAV bytes for STT upload."""
    with io.BytesIO() as buffer_io:
        with wave.open(buffer_io, "wb") as wav_file:
            wav_file.setnchannels(buffer.channels)
            wav_file.setsampwidth(buffer.sample_width)
            wav_file.setframerate(buffer.sample_rate)
            wav_file.writeframes(buffer.pcm_bytes)
        return buffer_io.getvalue()
