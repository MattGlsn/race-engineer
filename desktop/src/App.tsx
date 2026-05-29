import { useState } from "react";

import { AppShell } from "./components/layout/AppShell";
import type { AppView } from "./components/layout/SidebarNav";
import { TranscriptView } from "./components/transcript/TranscriptView";
import { FuelWidget } from "./components/widgets/FuelWidget";
import { GapWidget } from "./components/widgets/GapWidget";
import { LapTimingWidget } from "./components/widgets/LapTimingWidget";
import { PositionWidget } from "./components/widgets/PositionWidget";
import { useBridgeWebSocket } from "./hooks/useBridgeWebSocket";
import { useTranscriptStore } from "./hooks/useTranscriptStore";
import { isRaceDataLive } from "./utils/bridge";

export default function App() {
  const [activeView, setActiveView] = useState<AppView>("dashboard");
  const transcriptStore = useTranscriptStore();
  const bridge = useBridgeWebSocket({ onTranscript: transcriptStore.handleIncoming });
  const dataLive = isRaceDataLive(bridge);
  const raceState = dataLive ? bridge.raceState : null;

  return (
    <AppShell bridge={bridge} activeView={activeView} onNavigate={setActiveView}>
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
        />
      )}
    </AppShell>
  );
}
