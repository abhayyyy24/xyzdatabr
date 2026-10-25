"""Core analysis: pick the forecast a buyer would actually have had at decision
time, join it to actuals, and compute errors."""

import pandas as pd

UK_TZ = "Europe/London"


def _utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True)


def decision_cutoff(start_times: pd.Series, cutoff_hour: int) -> pd.Series:
    """For each target time, the UTC instant of the day-ahead decision:
    (delivery day - 1) at cutoff_hour, in UK local time."""
    local_day = (
        start_times.dt.tz_convert(UK_TZ).dt.tz_localize(None).dt.normalize()
    )
    cutoff_local = local_day - pd.Timedelta(days=1) + pd.Timedelta(hours=cutoff_hour)
    return cutoff_local.dt.tz_localize(
        UK_TZ, ambiguous="NaT", nonexistent="shift_forward"
    ).dt.tz_convert("UTC")


def select_decision_forecasts(forecasts: pd.DataFrame, cutoff_hour: int) -> pd.DataFrame:
    """One row per target half-hour: the latest forecast published on or before
    the decision cutoff. Forecasts published after the cutoff (including ones
    published after the target time itself) are excluded."""
    f = forecasts.copy()
    f["startTime"] = _utc(f["startTime"])
    f["publishTime"] = _utc(f["publishTime"])
    f["cutoff"] = decision_cutoff(f["startTime"], cutoff_hour)

    f = f[f["publishTime"] <= f["cutoff"]]
    f = f.sort_values(["startTime", "publishTime"]).drop_duplicates(
        "startTime", keep="last"
    )
    f["horizon_h"] = (f["startTime"] - f["publishTime"]).dt.total_seconds() / 3600
    f = f.rename(columns={"generation": "forecast"})
    return f[["startTime", "publishTime", "cutoff", "forecast", "horizon_h"]]


def build_decision_dataset(
    actuals: pd.DataFrame, forecasts: pd.DataFrame, cutoff_hour: int
) -> pd.DataFrame:
    """Actuals left-joined with the decision-time forecast. Targets with no
    available forecast keep NaN so coverage gaps stay visible.

    error = forecast - actual. Positive means the forecast was too high
    (wind over-predicted), so the buyer would under-procure from thermal."""
    a = actuals.copy()
    a["startTime"] = _utc(a["startTime"])
    a = a.rename(columns={"generation": "actual"})[["startTime", "actual"]]

    sel = select_decision_forecasts(forecasts, cutoff_hour)
    df = a.merge(sel, on="startTime", how="left")
    df["error"] = df["forecast"] - df["actual"]
    df["abs_error"] = df["error"].abs()
    return df.sort_values("startTime").reset_index(drop=True)