import { formatHotkeyLabel } from "../../utils/hotkeyCapture";

type VoiceRecordingIndicatorProps = {
  status: "recording" | "idle";
  hotkey: string;
};

export function VoiceRecordingIndicator({
  status,
  hotkey,
}: VoiceRecordingIndicatorProps) {
  if (status === "recording") {
    return (
      <div
        className="voice-recording-indicator voice-recording-indicator--active"
        role="status"
        aria-live="polite"
      >
        <span className="voice-recording-indicator__dot" aria-hidden="true" />
        <span className="voice-recording-indicator__text">Listening — speak now</span>
      </div>
    );
  }

  return (
    <p className="voice-recording-indicator voice-recording-indicator--idle" role="note">
      Hold <kbd>{formatHotkeyLabel(hotkey)}</kbd> on the bridge machine to record.
    </p>
  );
}
