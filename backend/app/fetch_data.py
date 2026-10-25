from .elexon import refresh_cache

if __name__ == "__main__":
    refresh_cache()
    print("Cached actuals and forecasts to backend/data/")