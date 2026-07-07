"""
src/demand_engine.py — AI Demand Forecasting Engine
Uses trained XGBoost model (demand_forecaster.pkl) with rule-based fallback.
"""
import os, datetime
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
}

_HOLIDAY_WEEKS = {9, 10, 11, 35, 36, 37}   # Fasika & Meskel


def forecast_demand(sector, product, region, historical_data=None):
    """
    Forecasts weekly demand in quintals and kg.
    Returns trend label and actionable recommendation.
    """
    art = _load_model()
    now = datetime.datetime.now()
    woy = now.isocalendar()[1]

    if art is not None:
        try:
            le   = art["label_encoder"]
            comm_key  = str(product).lower().strip()
            commodity = _COMMODITY_MAP.get(comm_key)

            # If product not in training commodities, pick closest
            if commodity not in le.classes_:
                commodity = le.classes_[0]

            # Derive lag features from historical_data if available
            if historical_data and len(historical_data) >= 4:
                vals      = [float(x) for x in historical_data[-4:]]
                lag1      = vals[-1]
                lag4      = vals[0]
                ma4       = float(np.mean(vals))
            else:
                lag1 = lag4 = ma4 = 300.0   # reasonable default (quintals)

            import pandas as pd
            row = pd.DataFrame([{
                "commodity_enc":      int(le.transform([commodity])[0]),
                "week":               woy % 52 or 52,
                "month":              now.month,
                "year":               now.year,
                "week_of_year":       woy,
                "is_holiday_week":    int(woy in _HOLIDAY_WEEKS),
                "is_harvest_season":  int(woy >= 40 or woy <= 5),
                "rainfall_lag1":      55.0,
                "price_lag1":         3000.0,
                "demand_lag1":        lag1,
                "demand_lag4":        lag4,
                "demand_ma4":         ma4,
            }])

            pred_qt  = float(art["model"].predict(row)[0])
            pred_qt  = max(pred_qt, 0)
            pred_kg  = pred_qt * 100

            # Trend vs lag
            trend_val = pred_qt - lag1
            if trend_val >  lag1 * 0.1:
                trend = "increasing"
            elif trend_val < -lag1 * 0.1:
                trend = "decreasing"
            else:
                trend = "stable"

            # Recommendation text
            if trend == "increasing":
                rec = (f"Demand for {product} is projected to RISE to "
                       f"{pred_qt:.0f} quintals this week. Consider increasing "
                       f"stock and listing more units to capture higher sales.")
            elif trend == "decreasing":
                rec = (f"Demand for {product} is expected to DECLINE to "
                       f"{pred_qt:.0f} quintals. Consider offering promotions "
                       f"or reducing listing price to move existing stock.")
            else:
                rec = (f"Demand for {product} is STABLE at ~{pred_qt:.0f} "
                       f"quintals/week. Maintain current stock and pricing strategy.")

            return {
                "predicted_demand":     round(pred_qt, 1),
                "predicted_demand_kg":  round(pred_kg, 1),
                "confidence_interval":  {
                    "lower": round(pred_qt * 0.82, 1),
                    "upper": round(pred_qt * 1.18, 1),
                },
                "trend":               trend,
                "is_holiday_week":     bool(woy in _HOLIDAY_WEEKS),
                "commodity_matched":   commodity,
                "model_r2":            art["metrics"]["r2"],
                "method":              "ml-xgboost",
                "recommendation":      rec,
            }
        except Exception:
            pass

    # ── Rule-based fallback ───────────────────────────────────
    base_demand = {"Agriculture": 120, "Livestock": 40, "Food Processing": 90}.get(sector, 80)
    return {
        "predicted_demand":    float(base_demand),
        "predicted_demand_kg": float(base_demand * 100),
        "confidence_interval": {"lower": base_demand * 0.75, "upper": base_demand * 1.25},
        "trend": "stable",
        "method": "rule-based-fallback",
        "recommendation": "Maintain current stock levels. Market demand is expected to remain stable.",
    }
