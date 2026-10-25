import { useEffect, useState } from "react";
import { fetchConfig, fetchDecisionView, fetchMetrics, fetchSweep } from "./api";
import type { AppConfig } from "./types";
import { useFetched } from "./useFetched";
import DecisionSection from "./components/DecisionSection";
import AccuracySection from "./components/AccuracySection";
import CutoffSection from "./components/CutoffSection";

export default function App() {
  const [cfg, setCfg] = useState<AppConfig | null>(null);
  const [configErr, setConfigErr] = useState<string | null>(null);
  const [cutoff, setCutoff] = useState(9);
  const [day, setDay] = useState("2026-01-28");
  const [start, setStart] = useState("2026-01-02");
  const [end, setEnd] = useState("2026-02-01");

  useEffect(() => {
    fetchConfig()
      .then((c) => {
        setCfg(c);
        setCutoff(c.default_cutoff_hour);
        setStart(c.window_start);
        setEnd(c.window_end);
      })
      .catch((e: Error) => setConfigErr(`Cannot reach backend: ${e.message}`));
  }, []);

  const ready = cfg !== null;
  const decision = useFetched(`d|${day}|${cutoff}`, ready, () => fetchDecisionView(day, cutoff));
  const metrics = useFetched(`m|${start}|${end}|${cutoff}`, ready, () =>
    fetchMetrics(start, end, cutoff)
  );
  const sweep = useFetched(`s|${start}|${end}`, ready, () => fetchSweep(start, end));

  const min = cfg?.window_start;
  const max = cfg?.window_end;

  return (
    <div className="app">
      <header>
        <h1>UK Wind Forecast Monitor</h1>
        <p>Day-ahead procurement support using Elexon national wind forecasts and actuals</p>
      </header>

      <div className="controls">
        <label>
          Decision hour (UK, day before)
          <select value={cutoff} onChange={(e) => setCutoff(Number(e.target.value))}>
            {Array.from({ length: 7 }, (_, i) => i + 6).map((h) => (
              <option key={h} value={h}>{String(h).padStart(2, "0")}:00</option>
            ))}
          </select>
        </label>
        <label>
          Delivery day
          <input type="date" value={day} min={min} max={max} onChange={(e) => setDay(e.target.value)} />
        </label>
        <label>
          Accuracy from
          <input type="date" value={start} min={min} max={max} onChange={(e) => setStart(e.target.value)} />
        </label>
        <label>
          to
          <input type="date" value={end} min={min} max={max} onChange={(e) => setEnd(e.target.value)} />
        </label>
      </div>

      {configErr && <p className="error">{configErr}</p>}

      {decision.loading && <p className="note">Loading decision view...</p>}
      {decision.error && <p className="error">Decision view: {decision.error}</p>}
      {decision.data && <DecisionSection data={decision.data} />}

      {metrics.loading && <p className="note">Loading accuracy...</p>}
      {metrics.error && <p className="error">Accuracy: {metrics.error}</p>}
      {metrics.data && <AccuracySection data={metrics.data} start={start} end={end} />}

      {sweep.data && <CutoffSection rows={sweep.data.results} />}
    </div>
  );
}