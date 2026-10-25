"""Error metrics on the decision-time dataset (see analysis.build_decision_dataset).
Convention: error = forecast - actual (positive = wind over-forecast)."""

import math

import pandas as pd

UK_TZ = "Europe/London"


def _num(x):
    if x is None:
        return None
    x = float(x)
    return None if math.isnan(x) else round(x, 2)


def summarize(df: pd.DataFrame) -> dict:
    d = df.dropna(subset=["forecast", "actual"])
    if d.empty:
        return {"n": 0}
    err = d["error"]
    abs_err = err.abs()
    mean_actual = d["actual"].mean()
    mae = abs_err.mean()
    return {
        "n": int(len(d)),
        "mean_actual_mw": _num(mean_actual),
        "mae_mw": _num(mae),
        "rmse_mw": _num(math.sqrt((err**2).mean())),
        "bias_mw": _num(err.mean()),
        "nmae_pct": _num(mae / mean_actual * 100) if mean_actual > 0 else None,
        "median_abs_error_mw": _num(abs_err.median()),
        "p90_abs_error_mw": _num(abs_err.quantile(0.90)),
        "error_p05_mw": _num(err.quantile(0.05)),
        "error_p95_mw": _num(err.quantile(0.95)),
    }


def by_hour_of_day(df: pd.DataFrame) -> list[dict]:
    d = df.dropna(subset=["forecast"]).copy()
    d["hour"] = d["startTime"].dt.tz_convert(UK_TZ).dt.hour
    out = []
    for hour, g in d.groupby("hour"):
        out.append({"hour": int(hour), **summarize(g)})
    return out


def by_day(df: pd.DataFrame) -> list[dict]:
    d = df.dropna(subset=["forecast"]).copy()
    d["day"] = d["startTime"].dt.tz_convert(UK_TZ).dt.date
    out = []
    for day, g in d.groupby("day"):
        out.append({"day": day.isoformat(), **summarize(g)})
    return out


def full_report(df: pd.DataFrame) -> dict:
    hourly = df[df["startTime"].dt.minute == 0]
    return {
        "coverage": {
            "half_hour_targets": int(len(df)),
            "hourly_targets": int(len(hourly)),
            "with_forecast": int(df["forecast"].notna().sum()),
            "missing_on_hourly_grid": int(hourly["forecast"].isna().sum()),
        },
        "overall": summarize(df),
        "by_hour": by_hour_of_day(df),
        "by_day": by_day(df),
    }