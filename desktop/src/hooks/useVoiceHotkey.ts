import { useCallback, useEffect, useRef, useState } from "react";

import { getVoiceHotkey, setVoiceHotkey } from "../utils/bridgeApi";
import { loadHotkey, saveHotkey } from "../utils/hotkeyStorage";

type UseVoiceHotkeyOptions = {
  bridgeConnected: boolean;
};

export function useVoiceHotkey({ bridgeConnected }: UseVoiceHotkeyOptions) {
  const [hotkey, setHotkey] = useState(() => loadHotkey());
  const [syncError, setSyncError] = useState<string | null>(null);
  const hotkeyRef = useRef(hotkey);

  useEffect(() => {
    hotkeyRef.current = hotkey;
  }, [hotkey]);

  const syncToBridge = useCallback(async (nextHotkey: string) => {
    const ok = await setVoiceHotkey(nextHotkey);
    setSyncError(
      ok ? null : "Could not update push-to-talk hotkey on the bridge.",
    );
    return ok;
  }, []);

  useEffect(() => {
    if (!bridgeConnected) {
      return;
    }

    let cancelled = false;

    const reconcile = async () => {
      const remote = await getVoiceHotkey();
      if (cancelled) {
        return;
      }

      if (remote?.hotkey) {
        setHotkey(remote.hotkey);
        saveHotkey(remote.hotkey);
        return;
      }

      await syncToBridge(hotkeyRef.current);
    };

    void reconcile();

    return () => {
      cancelled = true;
    };
  }, [bridgeConnected, syncToBridge]);

  const selectHotkey = useCallback(
    (nextHotkey: string) => {
      setHotkey(nextHotkey);
      saveHotkey(nextHotkey);
      setSyncError(null);
      if (bridgeConnected) {
        void syncToBridge(nextHotkey);
      }
    },
    [bridgeConnected, syncToBridge],
  );

  return { hotkey, selectHotkey, syncError };
}
