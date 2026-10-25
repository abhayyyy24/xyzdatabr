import pandas as pd

from app.analysis import build_decision_dataset, select_decision_forecasts


def _forecasts():
    target = "2026-01-02T12:00:00Z"
    return pd.DataFrame(
        {
            "startTime": [target] * 4,
            "publishTime": [
                "2026-01-01T04:30:00Z",  # before cutoff, older
                "2026-01-01T08:30:00Z",  # before cutoff, latest -> expected
                "2026-01-01T09:30:00Z",  # after cutoff (09:00)
                "2026-01-02T13:30:00Z",  # published after the target time
            ],
            "generation": [1000, 2000, 3000, 4000],
        }
    )


def test_picks_latest_forecast_before_cutoff():
    sel = select_decision_forecasts(_forecasts(), cutoff_hour=9)
    assert len(sel) == 1
    assert sel.iloc[0]["forecast"] == 2000
    assert sel.iloc[0]["horizon_h"] > 0


def test_missing_forecast_stays_nan():
    actuals = pd.DataFrame(
        {
            "startTime": ["2026-01-02T12:00:00Z", "2026-01-02T12:30:00Z"],
            "generation": [1800, 1900],
        }
    )
    df = build_decision_dataset(actuals, _forecasts(), cutoff_hour=9)
    assert df["forecast"].notna().sum() == 1
    assert df.loc[0, "error"] == 200  # forecast 2000 - actual 1800

def test_forecast_published_exactly_at_cutoff_is_included():
    f = pd.DataFrame(
        {
            "startTime": ["2026-01-02T12:00:00Z"] * 2,
            "publishTime": ["2026-01-01T08:30:00Z", "2026-01-01T09:00:00Z"],
            "generation": [1000, 2000],
        }
    )
    sel = select_decision_forecasts(f, cutoff_hour=9)
    assert sel.iloc[0]["forecast"] == 2000


def test_input_order_does_not_matter():
    shuffled = _forecasts().sample(frac=1, random_state=1)
    sel = select_decision_forecasts(shuffled, cutoff_hour=9)
    assert sel.iloc[0]["forecast"] == 2000


def test_only_late_forecasts_means_no_forecast():
    f = pd.DataFrame(
        {
            "startTime": ["2026-01-02T12:00:00Z"],
            "publishTime": ["2026-01-01T09:30:00Z"],
            "generation": [3000],
        }
    )
    assert select_decision_forecasts(f, cutoff_hour=9).empty