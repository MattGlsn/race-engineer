import { useCallback, useEffect, useRef, useState } from "react";

import { getVoiceVolume, setVoiceVolume } from "../utils/bridgeApi";
import {
  clampVoiceVolume,
  loadVoiceVolume,
  saveVoiceVolume,
} from "../utils/voiceVolumeStorage";

type UseVoiceVolumeOptions = {
  bridgeConnected: boolean;
};

export function useVoiceVolume({ bridgeConnected }: UseVoiceVolumeOptions) {
  const [volume, setVolume] = useState(() => loadVoiceVolume());
  const [syncError, setSyncError] = useState<string | null>(null);
  const volumeRef = useRef(volume);

  useEffect(() => {
    volumeRef.current = volume;
  }, [volume]);

  const syncToBridge = useCallback(async (nextVolume: number) => {
    const ok = await setVoiceVolume(nextVolume);
    setSyncError(
      ok ? null : "Could not update engineer volume on the bridge.",
    );
    return ok;
  }, []);

  useEffect(() => {
    if (!bridgeConnected) {
      return;
    }

    let cancelled = false;

    const reconcile = async () => {
      const remote = await getVoiceVolume();
      if (cancelled) {
        return;
      }

      if (remote?.volume != null) {
        const clamped = clampVoiceVolume(remote.volume);
        setVolume(clamped);
        saveVoiceVolume(clamped);
        return;
      }

      await syncToBridge(volumeRef.current);
    };

    void reconcile();

    return () => {
      cancelled = true;
    };
  }, [bridgeConnected, syncToBridge]);

  const setVolumeLevel = useCallback(
    (nextVolume: number) => {
      const clamped = clampVoiceVolume(nextVolume);
      setVolume(clamped);
      saveVoiceVolume(clamped);
      setSyncError(null);
      if (bridgeConnected) {
        void syncToBridge(clamped);
      }
    },
    [bridgeConnected, syncToBridge],
  );

  return { volume, setVolumeLevel, syncError };
}
