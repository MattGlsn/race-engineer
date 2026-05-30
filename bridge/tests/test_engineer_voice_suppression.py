from unittest.mock import MagicMock

from race_engineer.proactive.suppression import WorkloadMonitor
from race_engineer.proactive.suppression.braking import BrakingConfig
from race_engineer.proactive.suppression.workload import WorkloadConfig
from race_engineer.telemetry.models import TelemetrySnapshot
from race_engineer.voice.engineer import EngineerVoiceService
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.tts.models import SynthesisResult


def test_speak_defers_while_workload_is_high() -> None:
    tts_client = MagicMock()
    workload = WorkloadMonitor()
    workload.observe(
        TelemetrySnapshot(brake=0.5, steering=0.0, speed=30.0),
        now=0.0,
    )
    service = EngineerVoiceService(
        tts_client,
        workload_monitor=workload,
        speak_guard=MagicMock(claim=MagicMock(return_value=True)),
    )

    result = service.speak("Box this lap")

    assert result.success
    assert result.data == SynthesisResult(text="Box this lap")
    tts_client.synthesize_stream.assert_not_called()


def test_flush_pending_speech_plays_when_workload_drops() -> None:
    tts_client = MagicMock()
    tts_client.synthesize_stream.return_value = VoicePipelineResult.ok(
        MagicMock(read=MagicMock(return_value=b"")),
    )
    workload = WorkloadMonitor(
        WorkloadConfig(braking=BrakingConfig(hold_seconds=0.1)),
    )
    workload.observe(
        TelemetrySnapshot(brake=0.5, steering=0.0, speed=30.0),
        now=0.0,
    )
    service = EngineerVoiceService(
        tts_client,
        workload_monitor=workload,
        speak_guard=MagicMock(claim=MagicMock(return_value=True)),
        player=MagicMock(),
    )
    service.speak("Hold the line")
    workload.observe(
        TelemetrySnapshot(brake=0.0, steering=0.0, speed=30.0),
        now=0.2,
    )
    workload.observe(
        TelemetrySnapshot(brake=0.0, steering=0.0, speed=30.0),
        now=0.5,
    )

    service.flush_pending_speech()

    tts_client.synthesize_stream.assert_called_once_with("Hold the line")
