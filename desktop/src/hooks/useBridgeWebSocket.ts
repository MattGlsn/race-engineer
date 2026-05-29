import { useEffect, useRef, useState } from "react";

import type { BridgeMessage, ConnectionState, RaceStateData } from "../types/bridge";
import type { TranscriptMessageData } from "../types/transcript";

const DEFAULT_WS_URL = "ws://127.0.0.1:8000/ws";
const RECONNECT_MS = 2000;

export type BridgeSocketState = {
  bridgeConnected: boolean;
  sdkConnected: boolean;
  connectionState: string | null;
  raceState: RaceStateData | null;
  lastRaceStateAt: number | null;
  lastError: string | null;
};

type UseBridgeWebSocketOptions = {
  url?: string;
  onTranscript?: (data: TranscriptMessageData, ts: number) => void;
};

const initialState: BridgeSocketState = {
  bridgeConnected: false,
  sdkConnected: false,
  connectionState: null,
  raceState: null,
  lastRaceStateAt: null,
  lastError: null,
};

function parseMessage(raw: string): BridgeMessage | null {
  try {
    const parsed = JSON.parse(raw) as BridgeMessage;
    if (typeof parsed === "object" && parsed !== null && "type" in parsed) {
      return parsed;
    }
  } catch {
    return null;
  }
  return null;
}

function applyConnection(
  prev: BridgeSocketState,
  data: ConnectionState,
): BridgeSocketState {
  const sdkConnected = Boolean(data.sdk_connected);
  return {
    ...prev,
    bridgeConnected: true,
    sdkConnected,
    connectionState: data.state,
    lastError: null,
    raceState: sdkConnected ? prev.raceState : null,
    lastRaceStateAt: sdkConnected ? prev.lastRaceStateAt : null,
  };
}

export function useBridgeWebSocket({
  url = DEFAULT_WS_URL,
  onTranscript,
}: UseBridgeWebSocketOptions = {}): BridgeSocketState {
  const [state, setState] = useState<BridgeSocketState>(initialState);
  const reconnectTimer = useRef<number | null>(null);
  const onTranscriptRef = useRef(onTranscript);

  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let cancelled = false;

    const clearReconnect = () => {
      if (reconnectTimer.current != null) {
        window.clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };

    const scheduleReconnect = () => {
      clearReconnect();
      reconnectTimer.current = window.setTimeout(() => {
        if (!cancelled) {
          connect();
        }
      }, RECONNECT_MS);
    };

    const connect = () => {
      clearReconnect();
      socket = new WebSocket(url);

      socket.onopen = () => {
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          bridgeConnected: true,
          lastError: null,
        }));
      };

      socket.onmessage = (event) => {
        if (cancelled || typeof event.data !== "string") {
          return;
        }
        const message = parseMessage(event.data);
        if (!message) {
          return;
        }

        if (message.type === "connection") {
          setState((prev) => applyConnection(prev, message.data));
          return;
        }

        if (message.type === "race_state") {
          setState((prev) => ({
            ...prev,
            bridgeConnected: true,
            raceState: message.data,
            lastRaceStateAt: message.ts,
            lastError: null,
          }));
          return;
        }

        if (message.type === "transcript") {
          onTranscriptRef.current?.(message.data, message.ts);
        }
      };

      socket.onerror = () => {
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          lastError: "WebSocket error",
        }));
      };

      socket.onclose = () => {
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          bridgeConnected: false,
          sdkConnected: false,
          connectionState: null,
          raceState: null,
          lastRaceStateAt: null,
        }));
        scheduleReconnect();
      };
    };

    connect();

    return () => {
      cancelled = true;
      clearReconnect();
      socket?.close();
    };
  }, [url]);

  return state;
}
