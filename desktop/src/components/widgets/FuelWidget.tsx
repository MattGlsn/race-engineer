import type { RaceStateData } from "../../types/bridge";
import { formatLiters } from "../../utils/format";
import { WidgetCard } from "./WidgetCard";

type FuelWidgetProps = {
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

export function FuelWidget({ raceState }: FuelWidgetProps) {
  const consumption = raceState?.fuel_consumption;
  const projection = raceState?.fuel_projection;

  return (
    <WidgetCard title="Fuel">
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
