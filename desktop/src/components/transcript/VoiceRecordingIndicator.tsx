type VoiceRecordingIndicatorProps = {
  status: "recording" | "idle";
};

export function VoiceRecordingIndicator({ status }: VoiceRecordingIndicatorProps) {
  if (status !== "recording") {
    return null;
  }

  return (
    <div className="voice-recording-indicator" role="status" aria-live="polite">
      <span className="voice-recording-indicator__dot" aria-hidden="true" />
      <span className="voice-recording-indicator__text">Listening — speak now</span>
    </div>
  );
}
