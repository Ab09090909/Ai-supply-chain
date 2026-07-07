"""
src/price_engine.py — AI Price Recommendation Engine
Uses trained GradientBoosting model (price_predictor.pkl) with rule-based fallback.
"""
import os, datetime
import pandas as pd

# ── Model loader (lazy, cached) ───────────────────────────────
_price_model = None

def _load_model():
    global _price_model
    if _price_model is not None:
        return _price_model
    try:
        import joblib
        # Look next to this file, then project root, then models/
        for candidate in [
            os.path.join(os.path.dirname(__file__), "..", "models", "price_predictor.pkl"),
            os.path.join(os.path.dirname(__file__), "price_predictor.pkl"),
            "price_predictor.pkl",
            "models/price_predictor.pkl",
        ]:
            if os.path.exists(candidate):
                _price_model = joblib.load(candidate)
                return _price_model
    except Exception:
        pass
    return None

# ── Ethiopian commodity → PKL commodity mapping ───────────────
_COMMODITY_MAP = {
    # Agriculture
    "teff": "Teff", "maize": "Maize", "corn": "Maize",
    "wheat": "Wheat", "sorghum": "Sorghum", "barley": "Barley",
    "coffee": "Coffee", "sesame": "Sesame", "lentils": "Lentils",
    "chickpeas": "Chickpeas", "haricot beans": "Haricot Beans",
    "sunflower": "Sunflower", "niger seed": "Niger Seed",
    "chat": "Chat", "sugarcane": "Sugarcane",
    "mango": "Mango", "banana": "Banana",
    "potato": "Potato", "onion": "Onion", "tomato": "Tomato", "pepper": "Pepper",
}

_REGION_MAP = {
    "addis ababa": "Addis Ababa",
    "oromia": "Oromia", "amhara": "Amhara",
    "snnpr": "SNNP", "snnp": "SNNP", "sidama": "SNNP",
    "tigray": "Tigray", "dire dawa": "Dire Dawa",
    "harari": "Harari",
}

_SEASON_BY_MONTH = {
    1: "Bega", 2: "Bega", 3: "Belg", 4: "Belg",
    5: "Kiremt", 6: "Kiremt", 7: "Kiremt", 8: "Kiremt",
    9: "Meher", 10: "Meher", 11: "Meher", 12: "Bega"
}

_SECTOR_BASE = {
    "Agriculture": 150, "Livestock": 2500, "Handicrafts": 300,
    "Manufacturing": 400, "Food Processing": 250, "Textiles": 350, "Services": 200
}


def _current_season():
    return _SEASON_BY_MONTH.get(datetime.datetime.now().month, "Meher")


def recommend_price(sector, product, region, quality_grade, quantity):
    """
    Returns AI-powered price recommendation in ETB.
    Tries ML model first; falls back to rule-based logic.
    """
    art = _load_model()

    if art is not None:
        try:
            # Map inputs to model vocabulary
            comm_key  = str(product).lower().strip()
            commodity = _COMMODITY_MAP.get(comm_key, "Teff")

            reg_key   = str(region).lower().strip()
            reg_mapped = _REGION_MAP.get(reg_key, "Oromia")

            season = _current_season()
            market = "Merkato"   # default; no market input from UI

            # Grade → quality signals
            grade_up   = 1.0
            if "premium" in str(quality_grade).lower() or "a" in str(quality_grade).lower():
                grade_up = 1.25
            elif "c" in str(quality_grade).lower() or "economy" in str(quality_grade).lower():
                grade_up = 0.80

            # Normalize quantity to kg
            qty_kg = float(quantity) if quantity else 100.0

            row = pd.DataFrame([{
                "commodity":       commodity,
                "region":          reg_mapped,
                "season":          season,
                "market":          market,
                "quantity_kg":     qty_kg,
                "transport":       "Truck",
                "distance_km":     80,
                "humidity_pct":    60,
                "rainfall_mm":     50,
                "road_quality":    3,
                "market_days_ago": 3,
                "supply_index":    1.0,
                "demand_index":    1.0,
                "prev_week_price": art["base_prices"].get(commodity, 3000),
            }])

            raw_price = float(art["model"].predict(row)[0])
            price     = raw_price * grade_up
            per_unit  = price / 100   # per kg (model uses per-quintal)

            return {
                "recommended_price_birr": round(per_unit, 2),
                "price_per_quintal":      round(price, 2),
                "season":                 season,
                "commodity_matched":      commodity,
                "confidence":             0.94,
                "model_mae_birr":         art["metrics"]["mae_etb"],
                "method":                 "ml-gradient-boosting",
            }
        except Exception as e:
            pass   # fall through to rule-based

    # ── Rule-based fallback ───────────────────────────────────
    base  = _SECTOR_BASE.get(sector, 200)
    grade = {"A": 1.3, "B": 1.0, "C": 0.7,
             "premium": 1.4, "economy": 0.65}.get(
                 str(quality_grade).split()[0].lower(), 1.0)
    return {
        "recommended_price_birr": round(base * grade, 2),
        "confidence": 0.60,
        "method": "rule-based-fallback",
    }
