import { AppShell } from "./components/layout/AppShell";
import { FuelWidget } from "./components/widgets/FuelWidget";
import { GapWidget } from "./components/widgets/GapWidget";
import { LapTimingWidget } from "./components/widgets/LapTimingWidget";
import { PositionWidget } from "./components/widgets/PositionWidget";
import { useBridgeWebSocket } from "./hooks/useBridgeWebSocket";
import { isRaceDataLive } from "./utils/bridge";

export default function App() {
  const bridge = useBridgeWebSocket();
  const dataLive = isRaceDataLive(bridge);
  const raceState = dataLive ? bridge.raceState : null;

  return (
    <AppShell bridge={bridge}>
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
    </AppShell>
  );
}
