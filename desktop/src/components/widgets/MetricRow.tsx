type MetricRowProps = {
  label: string;
  value: string;
};

export function MetricRow({ label, value }: MetricRowProps) {
  return (
    <div className="metric-row">
      <span className="metric-row__label">{label}</span>
      <span className="metric-row__value">{value}</span>
    </div>
  );
}
