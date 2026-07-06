"""
src/fraud_engine.py — Fraud Detection Engine
"""

def check_fraud_risk(sector, product, region, payment_method, quantity, agreed_price_birr, market_price_birr):
    """
    Checks fraud risk. Uses rule-based fallback logic.
    """
    try:
        if market_price_birr and market_price_birr > 0:
            deviation = abs(agreed_price_birr - market_price_birr) / market_price_birr
        else:
            deviation = 0
            
        if deviation > 0.3:
            return {"risk_level": "High", "is_fraud": 1, "fraud_probability": 0.8}
        elif deviation > 0.15:
            return {"risk_level": "Medium", "is_fraud": 0, "fraud_probability": 0.4}
        else:
            return {"risk_level": "Low", "is_fraud": 0, "fraud_probability": 0.1}
    except Exception:
        return {"risk_level": "Low", "is_fraud": 0, "fraud_probability": 0.0}
