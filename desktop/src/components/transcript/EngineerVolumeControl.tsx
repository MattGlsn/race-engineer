import { MAX_VOICE_VOLUME, MIN_VOICE_VOLUME } from "../../utils/voiceVolumeStorage";

type EngineerVolumeControlProps = {
  volume: number;
  onChangeVolume: (volume: number) => void;
  syncError: string | null;
  bridgeConnected: boolean;
};

export function EngineerVolumeControl({
  volume,
  onChangeVolume,
  syncError,
  bridgeConnected,
}: EngineerVolumeControlProps) {
  const percent = Math.round(volume * 100);

  return (
    <div className="engineer-volume" aria-label="Engineer volume">
      <label className="engineer-volume__label" htmlFor="engineer-volume-slider">
        Engineer volume
        <span className="engineer-volume__value">{percent}%</span>
      </label>
      <input
        id="engineer-volume-slider"
        className="engineer-volume__slider"
        type="range"
        min={MIN_VOICE_VOLUME}
        max={MAX_VOICE_VOLUME}
        step={0.05}
        value={volume}
        onChange={(event) => onChangeVolume(Number.parseFloat(event.target.value))}
      />
      <p className="engineer-volume__hint">
        Raise above 100% to hear the engineer over engine noise. Playback runs on
        the bridge machine.
      </p>
      {!bridgeConnected ? (
        <p className="engineer-volume__hint">
          Connect to the bridge to apply volume to live voice replies.
        </p>
      ) : null}
      {syncError ? (
        <p className="engineer-volume__error" role="alert">
          {syncError}
        </p>
      ) : null}
    </div>
  );
}
