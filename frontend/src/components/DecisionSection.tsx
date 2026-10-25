import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { DecisionView } from "../types";
import { dateTimeLabel, mw, pct, signedMw, timeLabel } from "../format";
import Kpi from "./kpi";

export default function DecisionSection({ data }: { data: DecisionView }) {
  const chartData = data.points.map((p) => ({
    time: timeLabel(p.t),
    Forecast: p.forecast,
    Actual: p.actual,
  }));
  const a = data.day_accuracy;

  return (
    <section>
      <h2>Decision view: delivery on {data.delivery_date}</h2>
      <p className="note">
        Decision cutoff: <b>{dateTimeLabel(data.decision_cutoff_utc)}</b> (UK time, day before
        delivery). Forecast run{data.forecast_runs_used.length > 1 ? "s" : ""} available then:{" "}
        <b>{data.forecast_runs_used.map(dateTimeLabel).join(", ")}</b>.
      </p>

      <div className="kpi-row">
        <Kpi label="Mean error (bias)" value={signedMw(a.bias_mw)} hint="forecast minus actual" />
        <Kpi label="Mean absolute error" value={mw(a.mae_mw)} />
        <Kpi label="Normalised MAE" value={pct(a.nmae_pct)} hint="MAE / mean actual" />
        <Kpi label="95th percentile error" value={signedMw(a.error_p95_mw)} hint="exceeded 1 hour in 20" />
      </div>

      <div className="chart">
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" interval={2} />
            <YAxis tickFormatter={(v) => `${Math.round(Number(v) / 1000)} GW`} />
            <Tooltip formatter={(v: unknown) => mw(Number(v))} />
            <Legend />
            <Line type="monotone" dataKey="Forecast" stroke="#2563eb" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="Actual" stroke="#16a34a" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}