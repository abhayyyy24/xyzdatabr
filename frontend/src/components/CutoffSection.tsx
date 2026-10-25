import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { SweepRow } from "../types";
import { mw } from "../format";

const gw = (v: unknown) => `${(Number(v) / 1000).toFixed(1)} GW`;

export default function CutoffSection({ rows }: { rows: SweepRow[] }) {
  const data = rows.map((r) => ({
    cutoff: `${String(r.cutoff_hour).padStart(2, "0")}:00`,
    MAE: r.mae_mw,
    Bias: r.bias_mw,
  }));
  return (
    <section>
      <h2>Does deciding later help?</h2>
      <p className="note">
        Accuracy over the selected period if the purchase decision is made at each hour on the
        day before delivery. Later decisions can use fresher forecast runs.
      </p>
      <div className="chart">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 10, right: 20, left: 20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="cutoff" />
            <YAxis tickFormatter={gw} />
            <Tooltip formatter={(v: unknown) => (v == null ? "n/a" : mw(Number(v)))} />
            <Legend />
            <Bar dataKey="MAE" fill="#f59e0b" />
            <Bar dataKey="Bias" fill="#dc2626" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}