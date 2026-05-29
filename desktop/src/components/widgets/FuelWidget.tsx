import type { RaceStateData } from "../../types/bridge";
import { formatLiters } from "../../utils/format";
import { MetricRow } from "./MetricRow";
import { WidgetCard } from "./WidgetCard";

type FuelWidgetProps = {
  raceState: RaceStateData | null;
  dataLive: boolean;
};

export function FuelWidget({ raceState, dataLive }: FuelWidgetProps) {
  const consumption = raceState?.fuel_consumption;
  const projection = raceState?.fuel_projection;

  return (
    <WidgetCard title="Fuel" dataLive={dataLive}>
      <MetricRow
        label="Last lap use"
        value={formatLiters(consumption?.last_lap_usage)}
      />
      <MetricRow
        label="Rolling avg"
        value={formatLiters(consumption?.rolling_avg_usage)}
      />
      <MetricRow
        label="Laps left"
        value={
          projection?.laps_remaining != null
            ? String(projection.laps_remaining)
            : "—"
        }
      />
      <MetricRow
        label="Finish fuel"
        value={formatLiters(projection?.projected_finish_fuel)}
      />
      <MetricRow
        label="Risk"
        value={projection?.risk_level ?? "—"}
      />
    </WidgetCard>
  );
}
