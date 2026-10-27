# UK Wind Forecast Monitor

Web app that helps a UK energy utility's day-ahead desk (a) see the latest wind
generation forecast available when they must decide, and (b) quantify how accurate
those forecasts have been, using Elexon national-level data only.

- **Live app:** https://xyzdatabr-l11o.vercel.app
- **API (Swagger docs):** https://xyzdatabr.vercel.app/docs

> **AI usage:** This project was built with the assistance of Claude, which
> was used for design discussion and code generation in parts.

## What it does

- **Decision view:** for a chosen delivery day, shows the forecast run(s) available at the
  decision cutoff (day before, default 09:00 UK time), the resulting forecast curve versus
  actual wind, and that day's accuracy.
- **Accuracy:** MAE, RMSE, bias, normalised MAE, a suggested buffer (95th percentile error),
  plus breakdowns by delivery day and by hour of day.
- **Cutoff comparison:** accuracy if the decision is taken at each hour from 06:00 to 12:00.

## Data

Only Elexon BMRS, national level, wind only:

- Actuals: `FUELHH` stream, `fuelType=WIND` (`startTime`, `generation`), half-hourly.
- Forecasts: `WINDFOR` stream (`startTime`, `publishTime`, `generation`), hourly.

A snapshot is committed in `backend/data/` so the deployed app never depends on live API
calls. Refresh it with `python -m app.fetch_data` (from `backend/`).

## Method and assumptions

- **Decision rule:** for each target time on delivery day D, use the latest forecast with
  `publishTime <= (D-1 at cutoff hour, Europe/London time)`. Anything published later is
  excluded, including forecasts published after the target time, to avoid hindsight bias.
- **Cutoff hour:** default 09:00 on D-1. Auction deadlines vary by venue, so it is
  configurable (06:00 to 12:00 in the UI).
- **January 2026 scope:** delivery days 1 to 31 Jan 2026, i.e. decisions made 31 Dec 2025 to
  30 Jan 2026. Delivery on 1 Feb (decided 31 Jan) is not evaluated.
- **Resolution:** forecasts are hourly and actuals half-hourly, so accuracy is evaluated on
  on-the-hour timestamps only (744 points), with no interpolation.
- **Error:** `forecast - actual`. Positive means wind was over-forecast, so the buyer would
  under-procure from thermal plants.
- **nMAE** (MAE / mean actual) is used instead of MAPE, which is unstable when wind is low.
- **Suggested buffer** is the 95th percentile of the error: exceeded about 1 hour in 20.

## Key findings (cutoff 09:00, 1 to 31 Jan 2026)

- MAE about 2,127 MW (nMAE 18.4%), RMSE about 2,606 MW.
- Forecasts were biased high by about +1,852 MW on average; the bias was positive on 27 of
  31 days, and often the same sign all day.
- 95th percentile error about +5,351 MW. Worst day: 28 Jan (forecast about 11.1 GW against
  about 5.8 GW actual).
- Deciding later helps only modestly (MAE about 2,129 MW at 06:00 down to about 2,003 MW at
  12:00) and does not remove the bias, so a bias correction or buffer is the practical lever.

## Repository layout

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app and endpoints
│   │   ├── config.py        # settings (window, default cutoff, CORS)
│   │   ├── elexon.py        # Elexon client and CSV cache
│   │   ├── fetch_data.py    # CLI: refresh the data snapshot
│   │   ├── analysis.py      # decision-time forecast selection, error calculation
│   │   ├── metrics.py       # accuracy metrics and breakdowns
│   │   └── service.py       # cached dataset, date filtering, JSON helpers
│   ├── data/                # committed snapshot: actuals.csv, forecasts.csv
│   ├── tests/               # pytest suite (analysis, metrics, service, API)
│   ├── index.py             # Vercel entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React + TypeScript (Vite) + recharts
│   ├── src/
│   │   ├── App.tsx, api.ts, types.ts, format.ts, useFetched.ts
│   │   └── components/      # DecisionSection, AccuracySection, CutoffSection, Kpi
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Run without Docker

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
VITE_API_URL=http://localhost:8010 npm run dev       # PowerShell: $env:VITE_API_URL="http://localhost:8000"; npm run dev
```

## Tests

```bash
cd backend && python -m pytest -q
cd frontend && npm run build && npm run lint
```

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Liveness |
| `GET /api/config` | Analysis window and default cutoff |
| `GET /api/decision-view?delivery_date=&cutoff_hour=` | Forecast run used and curve for one delivery day |
| `GET /api/metrics?start=&end=&cutoff_hour=` | Accuracy metrics and breakdowns |
| `GET /api/cutoff-sweep?start=&end=` | Accuracy for each decision hour 06:00 to 12:00 |
| `GET /api/timeseries?start=&end=&cutoff_hour=` | Raw actual and forecast series |

## Deployment (Vercel)

Two Vercel projects from this repo: Root Directory `backend` (FastAPI, env
`ALLOW_LIVE_FETCH=false`) and Root Directory `frontend` (Vite, env `VITE_API_URL` set to the
backend URL).

## Limitations

- National totals only; no regional or site-level breakdown.
- One month of data, so accuracy statistics are indicative, not definitive.
- Hourly-only evaluation; half-hourly actuals without a forecast are not scored.
- Day-ahead auction timing is simplified to a single configurable cutoff hour.