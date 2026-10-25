from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_rejects_date_before_window():
    before = (date.fromisoformat(settings.window_start) - timedelta(days=1)).isoformat()
    assert client.get("/api/metrics", params={"start": before}).status_code == 422


def test_rejects_bad_cutoff_hour():
    assert client.get("/api/metrics", params={"cutoff_hour": 25}).status_code == 422


def test_metrics_smoke():
    body = client.get("/api/metrics").json()
    assert body["coverage"]["missing_on_hourly_grid"] == 0
    assert body["overall"]["n"] > 0