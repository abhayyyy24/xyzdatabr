from datetime import date
from functools import lru_cache

import pandas as pd

from .analysis import UK_TZ, build_decision_dataset
from .elexon import load_actuals, load_forecasts


@lru_cache(maxsize=24)
def get_dataset(cutoff_hour: int) -> pd.DataFrame:
    return build_decision_dataset(load_actuals(), load_forecasts(), cutoff_hour)


def filter_dates(df: pd.DataFrame, start: date | None, end: date | None) -> pd.DataFrame:
    """Keep rows whose UK-local delivery date is within [start, end]."""
    local_date = df["startTime"].dt.tz_convert(UK_TZ).dt.date
    mask = pd.Series(True, index=df.index)
    if start:
        mask &= local_date >= start
    if end:
        mask &= local_date <= end
    return df.loc[mask]


def _clean(v):
    return None if pd.isna(v) else float(v)


def to_points(df: pd.DataFrame) -> list[dict]:
    return [
        {
            "t": r.startTime.isoformat(),
            "actual": _clean(r.actual),
            "forecast": _clean(r.forecast),
            "error": _clean(r.error),
            "publish_time": None if pd.isna(r.publishTime) else r.publishTime.isoformat(),
            "horizon_h": _clean(r.horizon_h),
        }
        for r in df.itertuples(index=False)
    ]