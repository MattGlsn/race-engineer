import type { RaceStateData } from "../../types/bridge";
import { formatPosition } from "../../utils/format";
import { MetricRow } from "./MetricRow";
import { WidgetCard } from "./WidgetCard";

type PositionWidgetProps = {
  raceState: RaceStateData | null;
  dataLive: boolean;
};

export function PositionWidget({ raceState, dataLive }: PositionWidgetProps) {
  const player = raceState?.player;

  return (
    <WidgetCard title="Position" dataLive={dataLive}>
      <MetricRow
        label="Overall"
        value={formatPosition(
          player?.overall_position,
          player?.field_size,
        )}
      />
      <MetricRow
        label="Class"
        value={
          player?.class_position != null
            ? `P${player.class_position}`
            : "—"
        }
      />
      <MetricRow
        label="Car idx"
        value={
          player?.car_idx != null ? String(player.car_idx) : "—"
        }
      />
    </WidgetCard>
  );
}
