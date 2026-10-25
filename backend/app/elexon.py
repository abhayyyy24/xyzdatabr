"""Elexon BMRS client: fetches wind actuals (FUELHH) and forecasts (WINDFOR)
and caches them as CSV so the app doesn't depend on live API calls."""

import time
from datetime import date, timedelta
from pathlib import Path

import httpx
import pandas as pd

from .config import settings

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ACTUALS_CSV = DATA_DIR / "actuals.csv"
FORECASTS_CSV = DATA_DIR / "forecasts.csv"

CHUNK_DAYS = 7  # stream endpoints limit the query range, so fetch in small windows


def _chunks(start: date, end: date, days: int):
    """Yield (chunk_start, chunk_end) date pairs covering [start, end] inclusive."""
    cur = start
    while cur <= end:
        nxt = min(cur + timedelta(days=days - 1), end)
        yield cur, nxt
        cur = nxt + timedelta(days=1)


def _get_json(client: httpx.Client, path: str, params: dict, retries: int = 3) -> list:
    url = f"{settings.elexon_base_url}{path}"
    for attempt in range(retries):
        try:
            r = client.get(url, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else data.get("data", [])
        except (httpx.HTTPError, ValueError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    return []


def fetch_actuals(start: date, end: date) -> pd.DataFrame:
    rows: list[dict] = []
    with httpx.Client() as client:
        for c_start, c_end in _chunks(start, end, CHUNK_DAYS):
            rows += _get_json(
                client,
                "/datasets/FUELHH/stream",
                {
                    "settlementDateFrom": c_start.isoformat(),
                    "settlementDateTo": c_end.isoformat(),
                    "fuelType": "WIND",
                },
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["startTime", "generation"])
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    df = df[["startTime", "generation"]].drop_duplicates("startTime")
    return df.sort_values("startTime").reset_index(drop=True)


def fetch_forecasts(publish_from: date, publish_to: date) -> pd.DataFrame:
    rows: list[dict] = []
    with httpx.Client() as client:
        for c_start, c_end in _chunks(publish_from, publish_to, CHUNK_DAYS):
            rows += _get_json(
                client,
                "/datasets/WINDFOR/stream",
                {
                    "publishDateTimeFrom": f"{c_start.isoformat()}T00:00:00Z",
                    "publishDateTimeTo": f"{c_end.isoformat()}T23:59:59Z",
                },
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["startTime", "publishTime", "generation"])
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
    df = df[["startTime", "publishTime", "generation"]]
    df = df.drop_duplicates(["startTime", "publishTime"])
    return df.sort_values(["startTime", "publishTime"]).reset_index(drop=True)


def refresh_cache() -> None:
    """Download everything needed for the analysis window and save to CSV."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    w_start = date.fromisoformat(settings.window_start)
    w_end = date.fromisoformat(settings.window_end)

    actuals = fetch_actuals(w_start, w_end)
    actuals.to_csv(ACTUALS_CSV, index=False)

    # Forecasts for January targets can be published before 1 Jan,
    # so start the publish window earlier.
    forecasts = fetch_forecasts(w_start - timedelta(days=settings.forecast_lookback_days), w_end)
    forecasts.to_csv(FORECASTS_CSV, index=False)


def _require(path: Path) -> None:
    if path.exists():
        return
    if not settings.allow_live_fetch:
        raise RuntimeError(f"Data snapshot missing: {path.name}. Commit backend/data/*.csv.")
    refresh_cache()


def load_actuals() -> pd.DataFrame:
    _require(ACTUALS_CSV)
    return pd.read_csv(ACTUALS_CSV, parse_dates=["startTime"])


def load_forecasts() -> pd.DataFrame:
    _require(FORECASTS_CSV)
    return pd.read_csv(FORECASTS_CSV, parse_dates=["startTime", "publishTime"])