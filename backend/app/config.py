from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    window_start: str = "2026-01-01"
    window_end: str = "2026-01-31"
    default_cutoff_hour: int = 9
    forecast_lookback_days: int = 7
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    allow_live_fetch: bool = True
    cors_origin_regex: str = r"https://.*\.vercel\.app"

settings = Settings()