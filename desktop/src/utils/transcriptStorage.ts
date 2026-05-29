import type { TranscriptStoreState } from "../types/transcript";

const STORAGE_KEY = "race-engineer:transcript:v1";

export function loadTranscriptState(): TranscriptStoreState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as TranscriptStoreState;
    if (
      typeof parsed !== "object" ||
      parsed === null ||
      !Array.isArray(parsed.conversations)
    ) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function saveTranscriptState(state: TranscriptStoreState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore quota or privacy-mode errors.
  }
}
