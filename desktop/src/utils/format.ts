const EMPTY = "—";

export function formatGapSeconds(seconds: number | null | undefined): string {
  if (seconds == null || Number.isNaN(seconds)) {
    return EMPTY;
  }
  const sign = seconds >= 0 ? "+" : "";
  return `${sign}${seconds.toFixed(3)}s`;
}

export function formatLiters(value: number | null | undefined, digits = 2): string {
  if (value == null || Number.isNaN(value)) {
    return EMPTY;
  }
  return `${value.toFixed(digits)} L`;
}

export function formatLapTime(seconds: number | null | undefined): string {
  if (seconds == null || seconds <= 0 || Number.isNaN(seconds)) {
    return EMPTY;
  }
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds - minutes * 60;
  const whole = Math.floor(remainder);
  const millis = Math.round((remainder - whole) * 1000);
  return `${minutes}:${whole.toString().padStart(2, "0")}.${millis.toString().padStart(3, "0")}`;
}

export function formatPosition(
  position: number | null | undefined,
  fieldSize: number | null | undefined,
): string {
  if (position == null) {
    return EMPTY;
  }
  if (fieldSize != null && fieldSize > 0) {
    return `P${position} / ${fieldSize}`;
  }
  return `P${position}`;
}
