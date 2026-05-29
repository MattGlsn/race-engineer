import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";

import {
  captureHotkeyFromKeyboardEvent,
  formatHotkeyLabel,
} from "../../utils/hotkeyCapture";

type VoiceHotkeyControlProps = {
  hotkey: string;
  onSelectHotkey: (hotkey: string) => void;
  syncError: string | null;
  bridgeConnected: boolean;
};

export function VoiceHotkeyControl({
  hotkey,
  onSelectHotkey,
  syncError,
  bridgeConnected,
}: VoiceHotkeyControlProps) {
  const [capturing, setCapturing] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!capturing) {
      return;
    }

    buttonRef.current?.focus();
  }, [capturing]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLButtonElement>) => {
      if (!capturing) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();

      const captured = captureHotkeyFromKeyboardEvent(event.nativeEvent);
      if (captured === null) {
        setCapturing(false);
        return;
      }

      onSelectHotkey(captured);
      setCapturing(false);
    },
    [capturing, onSelectHotkey],
  );

  return (
    <div className="voice-hotkey" aria-label="Push-to-talk hotkey">
      <span className="voice-hotkey__label" id="voice-hotkey-label">
        Push-to-talk hotkey
      </span>
      <div className="voice-hotkey__row">
        <kbd className="voice-hotkey__binding">{formatHotkeyLabel(hotkey)}</kbd>
        <button
          ref={buttonRef}
          type="button"
          className="voice-hotkey__change"
          aria-labelledby="voice-hotkey-label"
          onClick={() => setCapturing(true)}
          onKeyDown={handleKeyDown}
          onBlur={() => setCapturing(false)}
        >
          {capturing ? "Press keys…" : "Change hotkey"}
        </button>
      </div>
      <p className="voice-hotkey__hint">
        Hold this key while speaking. Push-to-talk runs on the bridge machine.
        Include Ctrl or Shift to avoid accidental triggers.
      </p>
      {!bridgeConnected ? (
        <p className="voice-hotkey__hint">
          Connect to the bridge to apply the hotkey to live voice capture.
        </p>
      ) : null}
      {syncError ? (
        <p className="voice-hotkey__error" role="alert">
          {syncError}
        </p>
      ) : null}
    </div>
  );
}
