"""
src/demand_engine.py — AI Demand Forecasting Engine
Returns a list of weekly demand values (what the producer page expects).
"""
import os
import datetime
import numpy as np

_demand_model = None

def _load_model():
    global _demand_model
    if _demand_model is not None:
        return _demand_model
    try:
        import joblib
        for candidate in [
            os.path.join(os.path.dirname(__file__), "..", "models", "demand_forecaster.pkl"),
            os.path.join(os.path.dirname(__file__), "demand_forecaster.pkl"),
            "demand_forecaster.pkl",
            "models/demand_forecaster.pkl",
        ]:
            if os.path.exists(candidate):
                _demand_model = joblib.load(candidate)
                return _demand_model
    except Exception:
        pass
    return None

_COMMODITY_MAP = {
    "teff": "Teff", "maize": "Maize", "corn": "Maize",
    "wheat": "Wheat", "sorghum": "Sorghum", "barley": "Barley",
    "coffee": "Coffee", "sesame": "Sesame", "lentils": "Lentils",
    "chickpeas": "Chickpeas", "haricot beans": "Haricot Beans",
    "sunflower": "Sunflower", "niger seed": "Niger Seed",
    "chat": "Chat", "potato": "Potato", "onion": "Onion",
    # sector-level fallbacks
    "agriculture": "Teff", "livestock": "Maize",
    "food processing": "Wheat", "manufacturing": "Barley",
    "handicrafts": "Sesame", "textiles": "Cotton",
    "services": "Coffee",
}

_HOLIDAY_WEEKS = {9, 10, 11, 35, 36, 37}   # Fasika & Meskel

# Sector → base weekly demand (quintals)
_SECTOR_BASE = {
    "Agriculture": 450, "Livestock": 80, "Food Processing": 200,
    "Manufacturing": 150, "Handicrafts": 60, "Textiles": 120, "Services": 50,
}


def forecast_demand(sector="Agriculture", product=None, region="Oromia",
                    historical_data=None, horizon=12):
    """
    Returns a list of `horizon` weekly demand forecasts (quintals).
    This is the shape the producer page chart expects:
        result = [week1_demand, week2_demand, ..., weekN_demand]
    """
    art = _load_model()
    now = datetime.datetime.now()

    # Pick commodity from product name or sector
    comm_key  = str(product or sector).lower().strip()
    commodity = _COMMODITY_MAP.get(comm_key)

    if art is not None:
        try:
            import pandas as pd
            le = art["label_encoder"]

            if commodity not in le.classes_:
                commodity = le.classes_[0]

            # Seed lag from historical_data or defaults
            if historical_data and len(historical_data) >= 4:
                vals = [float(x) for x in historical_data[-4:]]
                lag1 = vals[-1]
                lag4 = vals[0]
                ma4  = float(np.mean(vals))
            else:
                base = _SECTOR_BASE.get(sector, 300)
                lag1 = lag4 = ma4 = float(base)

            weekly_forecast = []
            curr_lag1 = lag1
            curr_lag4 = lag4
            curr_ma4  = ma4

            for i in range(horizon):
                future_date = now + datetime.timedelta(weeks=i + 1)
                woy  = future_date.isocalendar()[1]
                row  = pd.DataFrame([{
                    "commodity_enc":      int(le.transform([commodity])[0]),
                    "week":               woy % 52 or 52,
                    "month":              future_date.month,
                    "year":              future_date.year,
                    "week_of_year":       woy,
                    "is_holiday_week":    int(woy in _HOLIDAY_WEEKS),
                    "is_harvest_season":  int(woy >= 40 or woy <= 5),
                    "rainfall_lag1":      55.0,
                    "price_lag1":         3000.0,
                    "demand_lag1":        curr_lag1,
                    "demand_lag4":        curr_lag4,
                    "demand_ma4":         curr_ma4,
                }])

                pred = float(art["model"].predict(row)[0])
                pred = max(pred, 0)
                weekly_forecast.append(round(pred, 1))

                # Roll lags forward
                curr_lag4 = curr_lag1
                curr_lag1 = pred
                curr_ma4  = float(np.mean(weekly_forecast[-4:]))

            return weekly_forecast

        except Exception:
            pass

    # ── Rule-based fallback ───────────────────────────────────
    base  = _SECTOR_BASE.get(sector, 200)
    woy_0 = now.isocalendar()[1]
    result = []
    for i in range(horizon):
        woy    = (woy_0 + i) % 52 or 52
        season = 1 + 0.25 * np.sin(2 * np.pi * woy / 52)
        holiday= 1.35 if woy in _HOLIDAY_WEEKS else 1.0
        noise  = np.random.normal(1.0, 0.05)
        result.append(round(base * season * holiday * noise, 1))
    return result
