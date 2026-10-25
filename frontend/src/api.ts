import type { AppConfig, DecisionView, MetricsResponse, SweepRow } from "./types";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function get<T>(path: string, params: Record<string, string | number> = {}): Promise<T> {
  const qs = new URLSearchParams(
    Object.entries(params).map(([k, v]) => [k, String(v)])
  ).toString();
  const res = await fetch(`${API}${path}${qs ? `?${qs}` : ""}`);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* keep statusText */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const fetchConfig = () => get<AppConfig>("/api/config");

export const fetchDecisionView = (deliveryDate: string, cutoffHour: number) =>
  get<DecisionView>("/api/decision-view", {
    delivery_date: deliveryDate,
    cutoff_hour: cutoffHour,
  });

export const fetchMetrics = (start: string, end: string, cutoffHour: number) =>
  get<MetricsResponse>("/api/metrics", { start, end, cutoff_hour: cutoffHour });

export const fetchSweep = (start: string, end: string) =>
  get<{ results: SweepRow[] }>("/api/cutoff-sweep", { start, end });