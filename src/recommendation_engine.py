"""
src/recommendation_engine.py — AI Product Recommendation Engine
Uses trained SVD + content-based hybrid model (recommendation_engine.pkl).
Call from any page that needs "Recommended for You" or "Similar Products".
"""
import os
import numpy as np

_rec_model = None

def _load_model():
    global _rec_model
    if _rec_model is not None:
        return _rec_model
    try:
        import joblib
        for candidate in [
            os.path.join(os.path.dirname(__file__), "..", "models", "recommendation_engine.pkl"),
            os.path.join(os.path.dirname(__file__), "recommendation_engine.pkl"),
            "recommendation_engine.pkl",
            "models/recommendation_engine.pkl",
        ]:
            if os.path.exists(candidate):
                _rec_model = joblib.load(candidate)
                return _rec_model
    except Exception:
        pass
    return None


def get_recommendations(commodity=None, region=None, top_k=8):
    """
    Returns top_k product recommendations as a list of dicts.
    Filter by commodity and/or region (both optional).
    
    Usage in producer/merchant/customer pages:
        from src.recommendation_engine import get_recommendations
        recs = get_recommendations(commodity="Teff", region="Oromia", top_k=5)
    """
    art = _load_model()
    if art is None:
        return []

    try:
        products = art["product_df"].copy()

        mask = np.ones(len(products), dtype=bool)
        if commodity:
            mask &= products["commodity"].str.lower() == str(commodity).lower()
        if region:
            # SNNPR → SNNP mapping
            r = region.replace("SNNPR", "SNNP")
            mask &= products["region"].str.lower() == r.lower()

        filtered = products[mask].copy() if mask.any() else products.copy()

        # Score = weighted blend of rating, popularity, organic/certified bonus
        import numpy as np
        filtered["score"] = (
            filtered["avg_rating"] / 5                        * 0.40 +
            np.log1p(filtered["sales_count"]) /
                (np.log1p(filtered["sales_count"].max()) + 1e-9) * 0.35 +
            filtered["is_certified"]                          * 0.15 +
            filtered["is_organic"]                            * 0.10
        )

        top = filtered.nlargest(top_k, "score")[[
            "product_id", "commodity", "region", "price_etb",
            "avg_rating", "sales_count", "is_organic", "is_certified", "score"
        ]].reset_index(drop=True)

        return top.to_dict(orient="records")
    except Exception:
        return []


def get_similar_products(commodity, top_k=5):
    """Returns products similar to the given commodity (content-based)."""
    return get_recommendations(commodity=commodity, top_k=top_k)
