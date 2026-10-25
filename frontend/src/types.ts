export interface Point {
  t: string;
  actual: number | null;
  forecast: number | null;
  error: number | null;
  publish_time: string | null;
  horizon_h: number | null;
}

export interface Summary {
  n: number;
  mean_actual_mw?: number | null;
  mae_mw?: number | null;
  rmse_mw?: number | null;
  bias_mw?: number | null;
  nmae_pct?: number | null;
  median_abs_error_mw?: number | null;
  p90_abs_error_mw?: number | null;
  error_p05_mw?: number | null;
  error_p95_mw?: number | null;
}

export interface MetricsResponse {
  cutoff_hour: number;
  coverage: {
    half_hour_targets: number;
    hourly_targets: number;
    with_forecast: number;
    missing_on_hourly_grid: number;
  };
  overall: Summary;
  by_hour: (Summary & { hour: number })[];
  by_day: (Summary & { day: string })[];
}

export interface DecisionView {
  delivery_date: string;
  decision_cutoff_utc: string;
  forecast_runs_used: string[];
  forecast_total_mwh: number;
  points: Point[];
  day_accuracy: Summary;
}

export interface AppConfig {
  window_start: string;
  window_end: string;
  default_cutoff_hour: number;
}

export interface SweepRow extends Summary {
  cutoff_hour: number;
}