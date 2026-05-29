import type { RaceStateData } from "../../types/bridge";
import { formatGapSeconds } from "../../utils/format";
import { WidgetCard } from "./WidgetCard";

type GapWidgetProps = {
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

export function GapWidget({ raceState }: GapWidgetProps) {
  const ahead = raceState?.gap_ahead;
  const behind = raceState?.gap_behind;

  return (
    <WidgetCard title="Gap">
      <MetricRow label="Ahead" value={formatGapSeconds(ahead?.gap_seconds)} />
      <MetricRow label="Behind" value={formatGapSeconds(behind?.gap_seconds)} />
      <MetricRow
        label="Dist ahead"
        value={
          ahead?.distance_meters != null
            ? `${ahead.distance_meters.toFixed(0)} m`
            : "—"
        }
      />
      <MetricRow
        label="Dist behind"
        value={
          behind?.distance_meters != null
            ? `${behind.distance_meters.toFixed(0)} m`
            : "—"
        }
      />
    </WidgetCard>
  );
}
