import pytest

from race_engineer.coaching.trace.compress import (
    compress_lap_trace,
    decompress_lap_trace,
    deserialize_samples,
    serialize_samples,
)
from race_engineer.coaching.trace.models import LapTrace, TraceSample


def _sample(index: int) -> TraceSample:
    return TraceSample(
        timestamp=float(index),
        lap_dist_pct=index / 100.0,
        speed=100.0 + index,
        fuel=30.0 - index,
        gear=3,
        throttle=0.8,
        brake=0.1,
        steering=0.2,
        rpm=6000.0 + index,
    )


def test_serialize_and_deserialize_round_trip() -> None:
    samples = tuple(_sample(index) for index in range(5))
    payload = serialize_samples(samples)
    restored = deserialize_samples(payload)
    assert restored == samples


def test_compress_and_decompress_round_trip() -> None:
    lap_trace = LapTrace(lap=2, samples=tuple(_sample(index) for index in range(10)))
    compressed = compress_lap_trace(lap_trace)
    restored = decompress_lap_trace(compressed)

    assert restored.lap == 2
    assert restored.samples == lap_trace.samples


def test_deserialize_rejects_invalid_magic() -> None:
    with pytest.raises(ValueError, match="invalid trace payload magic"):
        deserialize_samples(b"BAD\x00\x01\x00\x00\x00\x00")
