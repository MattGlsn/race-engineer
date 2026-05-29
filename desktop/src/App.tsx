import { AppShell } from "./components/layout/AppShell";
import { FuelWidget } from "./components/widgets/FuelWidget";
import { GapWidget } from "./components/widgets/GapWidget";
import { PositionWidget } from "./components/widgets/PositionWidget";
import { useBridgeWebSocket } from "./hooks/useBridgeWebSocket";

export default function App() {
  const bridge = useBridgeWebSocket();

  return (
    <AppShell bridge={bridge}>
      <div className="dashboard-grid">
        <div className="dashboard-grid__slot">
          <GapWidget raceState={bridge.raceState} />
        </div>
        <div className="dashboard-grid__slot">
          <PositionWidget raceState={bridge.raceState} />
        </div>
        <div className="dashboard-grid__slot">
          <FuelWidget raceState={bridge.raceState} />
        </div>
        <div className="dashboard-grid__slot" aria-hidden="true" />
      </div>
    </AppShell>
  );
}
