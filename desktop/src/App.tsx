import { useCallback, useState } from "react";

import { AppShell } from "./components/layout/AppShell";
import type { AppView } from "./components/layout/SidebarNav";
import { TranscriptView } from "./components/transcript/TranscriptView";
import { FuelWidget } from "./components/widgets/FuelWidget";
import { GapWidget } from "./components/widgets/GapWidget";
import { LapTimingWidget } from "./components/widgets/LapTimingWidget";
import { PositionWidget } from "./components/widgets/PositionWidget";
import { useBridgeWebSocket } from "./hooks/useBridgeWebSocket";
import { usePersonalitySettings } from "./hooks/usePersonalitySettings";
import { useVoiceHotkey } from "./hooks/useVoiceHotkey";
import { useVoiceVolume } from "./hooks/useVoiceVolume";
import { useTranscriptStore } from "./hooks/useTranscriptStore";
import type { TranscriptMessageData } from "./types/transcript";
import { isRaceDataLive } from "./utils/bridge";

export default function App() {
  const [activeView, setActiveView] = useState<AppView>("dashboard");
  const transcriptStore = useTranscriptStore();
  const onTranscript = useCallback(
    (data: TranscriptMessageData, ts: number) => {
      transcriptStore.handleIncoming(data, ts);
      setActiveView("transcript");
    },
    [transcriptStore.handleIncoming],
  );
  const bridge = useBridgeWebSocket({ onTranscript });
  const personality = usePersonalitySettings({
    bridgeConnected: bridge.bridgeConnected,
  });
  const voiceHotkey = useVoiceHotkey({ bridgeConnected: bridge.bridgeConnected });
  const voiceVolume = useVoiceVolume({ bridgeConnected: bridge.bridgeConnected });
  const dataLive = isRaceDataLive(bridge);
  const raceState = dataLive ? bridge.raceState : null;

  return (
    <AppShell
      bridge={bridge}
      activeView={activeView}
      onNavigate={setActiveView}
      personalityMode={personality.mode}
      onSelectPersonalityMode={personality.selectMode}
      personalitySyncError={personality.syncError}
      voiceHotkey={voiceHotkey.hotkey}
      onSelectVoiceHotkey={voiceHotkey.selectHotkey}
      voiceHotkeySyncError={voiceHotkey.syncError}
    >
      {activeView === "dashboard" ? (
        <div className="dashboard-grid">
          <div className="dashboard-grid__slot">
            <GapWidget dataLive={dataLive} raceState={raceState} />
          </div>
          <div className="dashboard-grid__slot">
            <PositionWidget dataLive={dataLive} raceState={raceState} />
          </div>
          <div className="dashboard-grid__slot">
            <FuelWidget dataLive={dataLive} raceState={raceState} />
          </div>
          <div className="dashboard-grid__slot">
            <LapTimingWidget dataLive={dataLive} raceState={raceState} />
          </div>
        </div>
      ) : (
        <TranscriptView
          conversations={transcriptStore.conversations}
          selectedConversation={transcriptStore.selectedConversation}
          selectedConversationId={transcriptStore.selectedConversationId}
          onSelectConversation={transcriptStore.selectConversation}
          voiceVolume={voiceVolume.volume}
          onChangeVoiceVolume={voiceVolume.setVolumeLevel}
          voiceVolumeSyncError={voiceVolume.syncError}
          bridgeConnected={bridge.bridgeConnected}
          voiceStatus={bridge.voiceStatus}
          voiceHotkey={voiceHotkey.hotkey}
        />
      )}
    </AppShell>
  );
}
