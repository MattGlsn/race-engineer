const STORAGE_KEY = "race-engineer:voice-volume:v1";
export const DEFAULT_VOICE_VOLUME = 1;
export const MAX_VOICE_VOLUME = 2;
export const MIN_VOICE_VOLUME = 0;

export function loadVoiceVolume(): number {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === null) {
      return DEFAULT_VOICE_VOLUME;
    }
    const parsed = Number.parseFloat(raw);
    if (Number.isFinite(parsed) && parsed >= MIN_VOICE_VOLUME && parsed <= MAX_VOICE_VOLUME) {
      return parsed;
    }
  } catch {
    // Ignore privacy-mode or quota errors.
  }
  return DEFAULT_VOICE_VOLUME;
}

export function saveVoiceVolume(volume: number): void {
  try {
    localStorage.setItem(STORAGE_KEY, String(volume));
  } catch {
    // Ignore privacy-mode or quota errors.
  }
}

export function clampVoiceVolume(volume: number): number {
  return Math.min(MAX_VOICE_VOLUME, Math.max(MIN_VOICE_VOLUME, volume));
}
