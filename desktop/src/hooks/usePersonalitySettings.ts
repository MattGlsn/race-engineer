import { useCallback, useEffect, useRef, useState } from "react";

import type { PersonalityMode } from "../types/personalityMode";
import { getPersonality, setPersonality } from "../utils/bridgeApi";
import {
  loadPersonalityMode,
  savePersonalityMode,
} from "../utils/personalityStorage";

type UsePersonalitySettingsOptions = {
  bridgeConnected: boolean;
};

export function usePersonalitySettings({
  bridgeConnected,
}: UsePersonalitySettingsOptions) {
  const [mode, setMode] = useState<PersonalityMode>(() => loadPersonalityMode());
  const [syncError, setSyncError] = useState<string | null>(null);
  const modeRef = useRef(mode);

  useEffect(() => {
    modeRef.current = mode;
  }, [mode]);

  const syncToBridge = useCallback(async (nextMode: PersonalityMode) => {
    const ok = await setPersonality(nextMode);
    setSyncError(ok ? null : "Could not update engineer tone on the bridge.");
    return ok;
  }, []);

  useEffect(() => {
    if (!bridgeConnected) {
      return;
    }

    let cancelled = false;

    const reconcile = async () => {
      const remote = await getPersonality();
      if (cancelled) {
        return;
      }

      if (remote?.mode) {
        setMode(remote.mode);
        savePersonalityMode(remote.mode);
        return;
      }

      await syncToBridge(modeRef.current);
    };

    void reconcile();

    return () => {
      cancelled = true;
    };
  }, [bridgeConnected, syncToBridge]);

  const selectMode = useCallback(
    (nextMode: PersonalityMode) => {
      setMode(nextMode);
      savePersonalityMode(nextMode);
      setSyncError(null);
      if (bridgeConnected) {
        void syncToBridge(nextMode);
      }
    },
    [bridgeConnected, syncToBridge],
  );

  return { mode, selectMode, syncError };
}
