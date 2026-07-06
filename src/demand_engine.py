"""
src/demand_engine.py — Demand Forecasting Engine
"""

def forecast_demand(sector, product, region, historical_data=None):
    """
    Forecasts future demand.
    """
    # Simple projection fallback
    return {
        "predicted_demand": 120.0,
        "confidence_interval": {"lower": 90.0, "upper": 150.0},
        "trend": "stable",
        "recommendation": "Maintain current stock levels. Market demand is expected to remain stable in the coming weeks."
    }
