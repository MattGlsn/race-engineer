import type { RaceStateData } from "../../types/bridge";
import { formatLapTime } from "../../utils/format";
import { findPlayerStanding } from "../../utils/raceState";
import { WidgetCard } from "./WidgetCard";

type LapTimingWidgetProps = {
  raceState: RaceStateData | null;
};

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-row">
      <span className="metric-row__label">{label}</span>
      <span className="metric-row__value">{value}</span>
    </div>
  );
}

export function LapTimingWidget({ raceState }: LapTimingWidgetProps) {
  const standing = findPlayerStanding(raceState);
  const track = raceState?.session.track_name;
  const sessionType = raceState?.session.session_type;

  return (
    <WidgetCard title="Lap timing">
      <MetricRow
        label="Best lap"
        value={formatLapTime(standing?.best_lap_time)}
      />
      <MetricRow
        label="Laps"
        value={standing?.laps != null ? String(standing.laps) : "—"}
      />
      <MetricRow label="Track" value={track?.trim() || "—"} />
      <MetricRow label="Session" value={sessionType?.trim() || "—"} />
    </WidgetCard>
  );
}
