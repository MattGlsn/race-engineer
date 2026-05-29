from unittest.mock import MagicMock

from race_engineer.voice.audio.player import AudioPlayer
from race_engineer.voice.audio.volume import VoiceVolumeConfig
from race_engineer.voice.engineer import EngineerVoiceService
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.tts.client import ElevenLabsTtsClient


def test_speak_streams_audio_to_player() -> None:
    tts_client = MagicMock(spec=ElevenLabsTtsClient)
    tts_client.synthesize_stream.return_value = VoicePipelineResult.ok(
        iter([b"\x00\x01"])
    )

    player = MagicMock(spec=AudioPlayer)
    service = EngineerVoiceService(
        tts_client,
        player=player,
        volume_config=VoiceVolumeConfig(volume=0.75),
    )

    result = service.speak("  box box  ")

    assert result.success
    assert result.data is not None
    assert result.data.text == "box box"
    player.play_stream.assert_called_once()
    chunks, kwargs = player.play_stream.call_args
    assert kwargs["volume"] == 0.75
    assert b"".join(chunks[0]) == b"\x00\x01"


def test_speak_propagates_tts_failure() -> None:
    tts_client = MagicMock(spec=ElevenLabsTtsClient)
    tts_client.synthesize_stream.return_value = VoicePipelineResult.fail(
        error_code=VoiceErrorCode.RATE_LIMIT,
        message="limited",
    )

    service = EngineerVoiceService(tts_client, player=MagicMock(spec=AudioPlayer))
    result = service.speak("hello")

    assert not result.success
    assert result.error_code == VoiceErrorCode.RATE_LIMIT
