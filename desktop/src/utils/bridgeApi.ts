import type { PersonalityMode } from "../types/personalityMode";

export const DEFAULT_BRIDGE_WS_URL = "ws://127.0.0.1:8000/ws";
export const DEFAULT_BRIDGE_HTTP_BASE = "http://127.0.0.1:8000";

export function bridgeHttpBase(wsUrl = DEFAULT_BRIDGE_WS_URL): string {
  try {
    const parsed = new URL(wsUrl);
    const protocol = parsed.protocol === "wss:" ? "https:" : "http:";
    return `${protocol}//${parsed.host}`;
  } catch {
    return DEFAULT_BRIDGE_HTTP_BASE;
  }
}

type PersonalityResponse = {
  mode: PersonalityMode;
};

export async function getPersonality(
  baseUrl = bridgeHttpBase(),
): Promise<PersonalityResponse | null> {
  try {
    const response = await fetch(`${baseUrl}/settings/personality`);
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as PersonalityResponse;
  } catch {
    return null;
  }
}

export async function setPersonality(
  mode: PersonalityMode,
  baseUrl = bridgeHttpBase(),
): Promise<boolean> {
  try {
    const response = await fetch(`${baseUrl}/settings/personality`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

type VoiceVolumeResponse = {
  volume: number;
};

export async function getVoiceVolume(
  baseUrl = bridgeHttpBase(),
): Promise<VoiceVolumeResponse | null> {
  try {
    const response = await fetch(`${baseUrl}/settings/volume`);
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as VoiceVolumeResponse;
  } catch {
    return null;
  }
}

export async function setVoiceVolume(
  volume: number,
  baseUrl = bridgeHttpBase(),
): Promise<boolean> {
  try {
    const response = await fetch(`${baseUrl}/settings/volume`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ volume }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

type VoiceHotkeyResponse = {
  hotkey: string;
};

export async function getVoiceHotkey(
  baseUrl = bridgeHttpBase(),
): Promise<VoiceHotkeyResponse | null> {
  try {
    const response = await fetch(`${baseUrl}/settings/hotkey`);
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as VoiceHotkeyResponse;
  } catch {
    return null;
  }
}

export async function setVoiceHotkey(
  hotkey: string,
  baseUrl = bridgeHttpBase(),
): Promise<boolean> {
  try {
    const response = await fetch(`${baseUrl}/settings/hotkey`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hotkey }),
    });
    return response.ok;
  } catch {
    return false;
  }
}
