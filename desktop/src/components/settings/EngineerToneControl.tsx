import {
  PERSONALITY_MODE_HINTS,
  PERSONALITY_MODE_LABELS,
  PERSONALITY_MODES,
  type PersonalityMode,
} from "../../types/personalityMode";

type EngineerToneControlProps = {
  mode: PersonalityMode;
  onSelectMode: (mode: PersonalityMode) => void;
  syncError: string | null;
  bridgeConnected: boolean;
};

export function EngineerToneControl({
  mode,
  onSelectMode,
  syncError,
  bridgeConnected,
}: EngineerToneControlProps) {
  return (
    <div className="engineer-tone" aria-label="Engineer tone">
      <span className="engineer-tone__label" id="engineer-tone-label">
        Engineer tone
      </span>
      <div
        className="engineer-tone__options"
        role="radiogroup"
        aria-labelledby="engineer-tone-label"
      >
        {PERSONALITY_MODES.map((option) => (
          <label key={option} className="engineer-tone__option">
            <input
              type="radio"
              name="engineer-tone"
              value={option}
              checked={mode === option}
              onChange={() => onSelectMode(option)}
            />
            <span className="engineer-tone__option-label">
              {PERSONALITY_MODE_LABELS[option]}
            </span>
            <span className="engineer-tone__option-hint">
              {PERSONALITY_MODE_HINTS[option]}
            </span>
          </label>
        ))}
      </div>
      {!bridgeConnected ? (
        <p className="engineer-tone__hint">
          Connect to the bridge to apply tone to live voice replies.
        </p>
      ) : null}
      {syncError ? (
        <p className="engineer-tone__error" role="alert">
          {syncError}
        </p>
      ) : null}
    </div>
  );
}
