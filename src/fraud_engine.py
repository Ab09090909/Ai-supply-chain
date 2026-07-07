"""
src/fraud_engine.py — AI Fraud Detection Engine
Uses trained RandomForest + SMOTE model (fraud_detector.pkl) with rule-based fallback.
"""
import os, datetime
import numpy as np

_fraud_model = None

def _load_model():
    global _fraud_model
    if _fraud_model is not None:
        return _fraud_model
    try:
        import joblib
        for candidate in [
            os.path.join(os.path.dirname(__file__), "..", "models", "fraud_detector.pkl"),
            os.path.join(os.path.dirname(__file__), "fraud_detector.pkl"),
            "fraud_detector.pkl",
            "models/fraud_detector.pkl",
        ]:
            if os.path.exists(candidate):
                _fraud_model = joblib.load(candidate)
                return _fraud_model
    except Exception:
        pass
    return None


def check_fraud_risk(sector, product, region, payment_method,
                     quantity, agreed_price_birr, market_price_birr,
                     account_age_days=365, tx_freq_week=2):
    """
    Returns fraud risk assessment dict.
    Keys: risk_level, is_fraud, fraud_probability, flags, method
    """
    art = _load_model()
    hour = datetime.datetime.now().hour

    if art is not None:
        try:
            import pandas as pd
            qty   = float(quantity) if quantity else 1.0
            price = float(agreed_price_birr) if agreed_price_birr else 0.0
            mkt   = float(market_price_birr) if market_price_birr else price

            dev = abs(price - mkt) / (mkt + 1)

            row = pd.DataFrame([{
                "quantity_kg":      qty * 100,           # convert quintals→kg
                "price_etb":        price,
                "price_deviation":  dev,
                "hour_of_day":      hour,
                "is_off_hours":     int(hour < 6 or hour > 20),
                "tx_freq_week":     tx_freq_week,
                "distance_km":      80,
                "account_age_days": account_age_days,
                "large_round_qty":  int(qty * 100 % 100 == 0 and qty * 100 > 1000),
                "new_account":      int(account_age_days < 30),
                "high_value":       int(qty * 100 * price > 500_000),
            }])

            prob      = float(art["model"].predict_proba(row)[0][1])
            threshold = art["threshold"]
            is_fraud  = prob > threshold

            # Collect human-readable flags
            flags = []
            if dev > 0.30:       flags.append(f"Price deviation {dev*100:.0f}% from market")
            if qty * 100 > 8000: flags.append("Unusually large quantity")
            if account_age_days < 30: flags.append("Very new account (<30 days)")
            if hour < 6 or hour > 20: flags.append("Transaction at unusual hour")
            if tx_freq_week > 30:     flags.append("Abnormally high transaction frequency")

            return {
                "risk_level":        "High" if prob > 0.70 else "Medium" if prob > threshold else "Low",
                "is_fraud":          int(is_fraud),
                "fraud_probability": round(prob, 4),
                "flags":             flags,
                "model_f1":          art["metrics"]["f1"],
                "method":            "ml-random-forest",
            }
        except Exception:
            pass

    # ── Rule-based fallback ───────────────────────────────────
    try:
        mkt = float(market_price_birr) if market_price_birr and float(market_price_birr) > 0 else float(agreed_price_birr)
        deviation = abs(float(agreed_price_birr) - mkt) / mkt
    except Exception:
        deviation = 0

    if deviation > 0.30:
        return {"risk_level": "High",   "is_fraud": 1, "fraud_probability": 0.80, "flags": [], "method": "rule-based-fallback"}
    elif deviation > 0.15:
        return {"risk_level": "Medium", "is_fraud": 0, "fraud_probability": 0.40, "flags": [], "method": "rule-based-fallback"}
    else:
        return {"risk_level": "Low",    "is_fraud": 0, "fraud_probability": 0.10, "flags": [], "method": "rule-based-fallback"}
