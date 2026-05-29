from unittest.mock import MagicMock

from race_engineer.voice.audio.player import AudioPlayer


def test_play_stream_writes_scaled_chunks_to_output() -> None:
    stream = MagicMock()
    stream_cm = MagicMock()
    stream_cm.__enter__.return_value = stream

    sd = MagicMock()
    sd.RawOutputStream.return_value = stream_cm

    player = AudioPlayer(sd=sd)
    player.play_stream([b"\x00\x10", b"\x00\x20"], volume=0.5)

    sd.RawOutputStream.assert_called_once()
    stream.start.assert_called_once()
    assert stream.write.call_count == 2
    stream.stop.assert_called_once()
    stream_cm.__exit__.assert_called_once()
