from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .metrics import full_report, summarize
from .service import filter_dates, get_dataset, to_points

app = FastAPI(title="Wind Forecast Analysis API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_methods=["*"],
    allow_headers=["*"],
)

WINDOW_START = date.fromisoformat(settings.window_start)
WINDOW_END = date.fromisoformat(settings.window_end)

CutoffHour = Query(default=settings.default_cutoff_hour, ge=0, le=23,
                   description="Decision hour (UK time) on the day before delivery")


def _check_range(start: date | None, end: date | None) -> None:
    for d in (start, end):
        if d and not (WINDOW_START <= d <= WINDOW_END):
            raise HTTPException(
                status_code=422,
                detail=f"Dates must be within {WINDOW_START} and {WINDOW_END}",
            )
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start must be on or before end")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/config")
def config():
    return {
        "window_start": settings.window_start,
        "window_end": settings.window_end,
        "default_cutoff_hour": settings.default_cutoff_hour,
    }


@app.get("/api/timeseries")
def timeseries(
    start: date | None = None,
    end: date | None = None,
    cutoff_hour: int = CutoffHour,
):
    """Actual wind and the decision-time forecast, half-hourly. Forecast is null
    on :30 slots because WINDFOR is hourly."""
    _check_range(start, end)
    df = filter_dates(get_dataset(cutoff_hour), start, end)
    return {"cutoff_hour": cutoff_hour, "points": to_points(df)}


@app.get("/api/decision-view")
def decision_view(delivery_date: date, cutoff_hour: int = CutoffHour):
    """What the buyer knew when deciding for one delivery day: which forecast
    run(s) were the latest available, and the resulting hourly curve."""
    _check_range(delivery_date, delivery_date)
    day = filter_dates(get_dataset(cutoff_hour), delivery_date, delivery_date)
    hourly = day.dropna(subset=["forecast"])
    if hourly.empty:
        raise HTTPException(status_code=404, detail="No forecast available for that day")
    return {
        "delivery_date": delivery_date.isoformat(),
        "decision_cutoff_utc": hourly["cutoff"].iloc[0].isoformat(),
        "forecast_runs_used": sorted(t.isoformat() for t in hourly["publishTime"].unique()),
        "forecast_total_mwh": round(float(hourly["forecast"].sum()), 1),
        "points": to_points(hourly),
        "day_accuracy": summarize(day),
    }


@app.get("/api/metrics")
def metrics(
    start: date | None = None,
    end: date | None = None,
    cutoff_hour: int = CutoffHour,
):
    _check_range(start, end)
    df = filter_dates(get_dataset(cutoff_hour), start, end)
    return {"cutoff_hour": cutoff_hour, **full_report(df)}

@app.get("/api/cutoff-sweep")
def cutoff_sweep(start: date | None = None, end: date | None = None):
    """Overall accuracy for each realistic decision hour (06:00-12:00)."""
    _check_range(start, end)
    results = []
    for h in range(6, 13):
        df = filter_dates(get_dataset(h), start, end)
        results.append({"cutoff_hour": h, **summarize(df)})
    return {"results": results}