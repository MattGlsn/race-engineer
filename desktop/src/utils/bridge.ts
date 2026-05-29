import type { BridgeSocketState } from "../hooks/useBridgeWebSocket";

export function isRaceDataLive(bridge: BridgeSocketState): boolean {
  return (
    bridge.bridgeConnected &&
    bridge.sdkConnected &&
    bridge.raceState != null
  );
}
