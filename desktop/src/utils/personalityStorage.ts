import {
  DEFAULT_PERSONALITY_MODE,
  type PersonalityMode,
  isPersonalityMode,
} from "../types/personalityMode";

const STORAGE_KEY = "race-engineer:personality:v1";

export function loadPersonalityMode(): PersonalityMode {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw && isPersonalityMode(raw)) {
      return raw;
    }
  } catch {
    // Ignore privacy-mode or quota errors.
  }
  return DEFAULT_PERSONALITY_MODE;
}

export function savePersonalityMode(mode: PersonalityMode): void {
  try {
    localStorage.setItem(STORAGE_KEY, mode);
  } catch {
    // Ignore privacy-mode or quota errors.
  }
}
