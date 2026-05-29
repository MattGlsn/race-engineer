import type { BridgeSocketState } from "../../hooks/useBridgeWebSocket";

type StatusCardsProps = {
  bridge: BridgeSocketState;
};

function formatRaceStateAge(ts: number | null): string {
  if (ts == null) {
    return "No data";
  }
  const ageSeconds = Math.max(0, Math.round(Date.now() / 1000 - ts));
  if (ageSeconds === 0) {
    return "Just now";
  }
  return `${ageSeconds}s ago`;
}

export function StatusCards({ bridge }: StatusCardsProps) {
  const bridgeTone = bridge.bridgeConnected ? "ok" : "error";
  const sdkTone = bridge.sdkConnected ? "ok" : bridge.bridgeConnected ? "warn" : "error";
  const raceTone =
    bridge.bridgeConnected && bridge.sdkConnected && bridge.lastRaceStateAt != null
      ? "ok"
      : bridge.bridgeConnected
        ? "warn"
        : "error";

  return (
    <div className="status-cards">
      <div className={`status-card status-card--${bridgeTone}`}>
        <span className="status-card__label">Bridge</span>
        <span className="status-card__value">
          {bridge.bridgeConnected ? "Connected" : "Disconnected"}
        </span>
      </div>
      <div className={`status-card status-card--${sdkTone}`}>
        <span className="status-card__label">iRacing SDK</span>
        <span className="status-card__value">
          {bridge.sdkConnected
            ? "Connected"
            : bridge.connectionState ?? "Unknown"}
        </span>
      </div>
      <div className={`status-card status-card--${raceTone}`}>
        <span className="status-card__label">Race state</span>
        <span className="status-card__value">
          {!bridge.bridgeConnected
            ? "Disconnected"
            : !bridge.sdkConnected
              ? "Waiting for SDK"
              : formatRaceStateAge(bridge.lastRaceStateAt)}
        </span>
      </div>
      {bridge.lastError ? (
        <div className="status-card status-card--error">
          <span className="status-card__label">Error</span>
          <span className="status-card__value">{bridge.lastError}</span>
        </div>
      ) : null}
    </div>
  );
}
