from datetime import date

import pandas as pd

from app.service import filter_dates, to_points


def _df():
    return pd.DataFrame(
        {
            "startTime": pd.to_datetime(
                ["2026-01-01T12:00:00Z", "2026-01-02T12:00:00Z", "2026-01-03T12:00:00Z"],
                utc=True,
            ),
            "actual": [1.0, 2.0, 3.0],
            "forecast": [1.5, None, 3.5],
            "error": [0.5, None, 0.5],
            "publishTime": pd.to_datetime(["2025-12-31T07:30:00Z", None, "2026-01-02T07:30:00Z"], utc=True),
            "horizon_h": [28.5, None, 28.5],
        }
    )


def test_filter_dates_inclusive():
    out = filter_dates(_df(), date(2026, 1, 2), date(2026, 1, 3))
    assert len(out) == 2


def test_to_points_nulls_are_none():
    pts = to_points(_df())
    assert pts[1]["forecast"] is None
    assert pts[1]["publish_time"] is None
    assert pts[0]["forecast"] == 1.5