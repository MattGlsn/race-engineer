import struct
import zlib

from race_engineer.coaching.trace.models import CompressedLapTrace, LapTrace, TraceSample

_TRACE_MAGIC = b"RTRC"
_TRACE_VERSION = 1
_HEADER = struct.Struct("<4sBI")
_SAMPLE = struct.Struct("<ddddidddd")


def serialize_samples(samples: tuple[TraceSample, ...]) -> bytes:
    """Serialize lap samples to a compact binary payload."""
    header = _HEADER.pack(_TRACE_MAGIC, _TRACE_VERSION, len(samples))
    body = b"".join(
        _SAMPLE.pack(
            sample.timestamp,
            sample.lap_dist_pct,
            sample.speed,
            sample.fuel,
            sample.gear,
            sample.throttle,
            sample.brake,
            sample.steering,
            sample.rpm,
        )
        for sample in samples
    )
    return header + body


def deserialize_samples(payload: bytes) -> tuple[TraceSample, ...]:
    """Deserialize a binary lap trace payload into samples."""
    if len(payload) < _HEADER.size:
        raise ValueError("trace payload too short")

    magic, version, sample_count = _HEADER.unpack_from(payload)
    if magic != _TRACE_MAGIC:
        raise ValueError("invalid trace payload magic")
    if version != _TRACE_VERSION:
        raise ValueError(f"unsupported trace payload version: {version}")

    expected_size = _HEADER.size + sample_count * _SAMPLE.size
    if len(payload) != expected_size:
        raise ValueError("trace payload size mismatch")

    offset = _HEADER.size
    samples: list[TraceSample] = []
    for _ in range(sample_count):
        values = _SAMPLE.unpack_from(payload, offset)
        offset += _SAMPLE.size
        samples.append(
            TraceSample(
                timestamp=values[0],
                lap_dist_pct=values[1],
                speed=values[2],
                fuel=values[3],
                gear=values[4],
                throttle=values[5],
                brake=values[6],
                steering=values[7],
                rpm=values[8],
            )
        )
    return tuple(samples)


def compress_lap_trace(lap_trace: LapTrace) -> CompressedLapTrace:
    """Compress a lap trace for storage."""
    payload = serialize_samples(lap_trace.samples)
    return CompressedLapTrace(
        lap=lap_trace.lap,
        sample_count=len(lap_trace.samples),
        data=zlib.compress(payload, level=6),
    )


def decompress_lap_trace(compressed: CompressedLapTrace) -> LapTrace:
    """Decompress a stored lap trace."""
    payload = zlib.decompress(compressed.data)
    samples = deserialize_samples(payload)
    if len(samples) != compressed.sample_count:
        raise ValueError("compressed sample count mismatch")
    return LapTrace(lap=compressed.lap, samples=samples)
