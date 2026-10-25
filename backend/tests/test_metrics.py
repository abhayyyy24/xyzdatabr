import pandas as pd

from app.metrics import summarize


def _df():
    return pd.DataFrame(
        {
            "startTime": pd.date_range("2026-01-02", periods=4, freq="30min", tz="UTC"),
            "actual": [1000.0, 1000.0, 1000.0, 1000.0],
            "forecast": [1100.0, 900.0, 1300.0, 1000.0],
            "horizon_h": [20.0] * 4,
        }
    ).assign(error=lambda d: d["forecast"] - d["actual"])


def test_summary_values():
    s = summarize(_df())
    assert s["n"] == 4
    assert s["mae_mw"] == 125.0           # (100+100+300+0)/4
    assert s["bias_mw"] == 75.0           # (100-100+300+0)/4
    assert s["nmae_pct"] == 12.5


def test_summary_ignores_missing_forecasts():
    df = _df()
    df.loc[0, "forecast"] = float("nan")
    df.loc[0, "error"] = float("nan")
    assert summarize(df)["n"] == 3


def test_empty():
    assert summarize(_df().iloc[0:0]) == {"n": 0}