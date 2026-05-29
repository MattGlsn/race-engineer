export const DEFAULT_VOICE_HOTKEY = "ctrl+shift+space";

const STORAGE_KEY = "race-engineer:hotkey:v1";

export function loadHotkey(): string {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw && raw.trim()) {
      return raw.trim().toLowerCase();
    }
  } catch {
    // Ignore privacy-mode or quota errors.
  }
  return DEFAULT_VOICE_HOTKEY;
}

export function saveHotkey(hotkey: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, hotkey);
  } catch {
    // Ignore privacy-mode or quota errors.
  }
}
