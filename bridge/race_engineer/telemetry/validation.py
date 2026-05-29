from race_engineer.telemetry.models import TelemetrySnapshot

_MAX_SPEED_MPS = 500.0
_MAX_RPM = 50_000.0
_MAX_STEERING_RAD = 10.0


def validate_snapshot(snapshot: TelemetrySnapshot) -> list[str]:
    """Return human-readable validation errors; empty list means valid."""
    errors: list[str] = []

    if snapshot.speed is not None and not 0 <= snapshot.speed <= _MAX_SPEED_MPS:
        errors.append(f"speed out of range: {snapshot.speed}")
    if snapshot.fuel is not None and snapshot.fuel < 0:
        errors.append(f"fuel out of range: {snapshot.fuel}")
    if snapshot.lap_dist_pct is not None and not 0 <= snapshot.lap_dist_pct <= 1:
        errors.append(f"lap_dist_pct out of range: {snapshot.lap_dist_pct}")
    if snapshot.gear is not None and not -1 <= snapshot.gear <= 8:
        errors.append(f"gear out of range: {snapshot.gear}")
    if snapshot.throttle is not None and not 0 <= snapshot.throttle <= 1:
        errors.append(f"throttle out of range: {snapshot.throttle}")
    if snapshot.brake is not None and not 0 <= snapshot.brake <= 1:
        errors.append(f"brake out of range: {snapshot.brake}")
    if snapshot.steering is not None and abs(snapshot.steering) > _MAX_STEERING_RAD:
        errors.append(f"steering out of range: {snapshot.steering}")
    if snapshot.rpm is not None and not 0 <= snapshot.rpm <= _MAX_RPM:
        errors.append(f"rpm out of range: {snapshot.rpm}")

    return errors


def is_valid_snapshot(snapshot: TelemetrySnapshot) -> bool:
    return not validate_snapshot(snapshot)
