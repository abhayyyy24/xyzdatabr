import {
  Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { MetricsResponse } from "../types";
import { mw, pct, signedMw } from "../format";
import Kpi from "./kpi";

const gw = (v: unknown) => `${(Number(v) / 1000).toFixed(1)} GW`;

export default function AccuracySection({ data, start, end }: {
  data: MetricsResponse; start: string; end: string;
}) {
  const o = data.overall;
  const dayData = data.by_day.map((d) => ({
    day: d.day.slice(5),
    MAE: d.mae_mw,
    Bias: d.bias_mw,
  }));
  const hourData = data.by_hour.map((h) => ({
    hour: `${String(h.hour).padStart(2, "0")}:00`,
    MAE: h.mae_mw,
    Bias: h.bias_mw,
  }));

  return (
    <section>
      <h2>Forecast accuracy: {start} to {end}</h2>
      <p className="note">
        Evaluated on {data.coverage.with_forecast} hourly points. Forecasts are hourly and actuals
        half-hourly, so only on-the-hour slots are compared (no interpolation). Error = forecast
        minus actual; positive means wind was over-forecast, so the buyer would under-procure.
      </p>

      <div className="kpi-row">
        <Kpi label="MAE" value={mw(o.mae_mw)} hint={`nMAE ${pct(o.nmae_pct)}`} />
        <Kpi label="RMSE" value={mw(o.rmse_mw)} />
        <Kpi label="Bias" value={signedMw(o.bias_mw)} hint="average over-forecast if positive" />
        <Kpi
          label="Suggested buffer"
          value={mw(o.error_p95_mw)}
          hint="95th percentile of error: exceeded 1 hour in 20"
        />
        <Kpi label="Mean actual wind" value={mw(o.mean_actual_mw)} />
      </div>

      <h3>By delivery day (GW)</h3>
      <div className="chart">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={dayData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis tickFormatter={gw} />
            <Tooltip formatter={(v: unknown) => mw(Number(v))} />
            <Legend />
            <Bar dataKey="MAE" fill="#f59e0b" />
            <Bar dataKey="Bias" fill="#dc2626" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <h3>By hour of day (GW)</h3>
      <div className="chart">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={hourData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" interval={2} />
            <YAxis tickFormatter={gw} />
            <Tooltip formatter={(v: unknown) => mw(Number(v))} />
            <Legend />
            <Line type="monotone" dataKey="MAE" stroke="#f59e0b" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="Bias" stroke="#dc2626" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}