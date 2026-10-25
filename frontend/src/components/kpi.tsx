interface Props {
  label: string;
  value: string;
  hint?: string;
}

export default function Kpi({ label, value, hint }: Props) {
  return (
    <div className="kpi">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {hint && <div className="kpi-hint">{hint}</div>}
    </div>
  );
}