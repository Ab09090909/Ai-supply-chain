"""
src/matching_engine.py — AI Merchant Matching Engine
Uses trained cosine-similarity model (merchant_matcher.pkl).
Falls back to rule-based scoring if model unavailable.
"""
import os

_match_model = None

def _load_model():
    global _match_model
    if _match_model is not None:
        return _match_model
    try:
        import joblib
        for candidate in [
            os.path.join(os.path.dirname(__file__), "..", "models", "merchant_matcher.pkl"),
            os.path.join(os.path.dirname(__file__), "merchant_matcher.pkl"),
            "merchant_matcher.pkl",
            "models/merchant_matcher.pkl",
        ]:
            if os.path.exists(candidate):
                _match_model = joblib.load(candidate)
                return _match_model
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
}

_REGION_MAP = {
    "addis ababa": "Addis Ababa",
    "oromia": "Oromia", "amhara": "Amhara",
    "snnpr": "SNNP", "snnp": "SNNP", "sidama": "SNNP",
    "tigray": "Tigray", "dire dawa": "Dire Dawa",
    "harari": "Harari",
}


def rank_merchants(listing_data, merchant_list):
    """
    Ranks merchants using ML model profiles first, then falls back
    to scoring the supplied merchant_list from Supabase.

    listing_data keys: sector, product, region, price_birr, quantity
    merchant_list: list of dicts from Supabase (merchant_preferences table)

    Returns list of dicts with match_probability added, sorted desc.
    """
    art = _load_model()

    # ── ML model path: use pre-trained merchant profiles ─────
    if art is not None:
        try:
            profiles  = art["merchant_profiles"].copy()
            weights   = art["weights"]

            comm_key  = str(listing_data.get("product", "")).lower().strip()
            commodity = _COMMODITY_MAP.get(comm_key, "Teff")
            comm_col  = f"spec_{commodity.lower().replace(' ', '_')}"

            reg_key   = str(listing_data.get("region", "")).lower().strip()
            region    = _REGION_MAP.get(reg_key, "Oromia")

            qty_qt    = float(listing_data.get("quantity", 100))
            price     = float(listing_data.get("price_birr", 0))

            scores = (
                profiles["avg_rating"]          / 5   * weights["rating"] +
                profiles["completion_rate"]            * weights["completion_rate"] +
                (1 - profiles["avg_delivery_days"].clip(0, 30) / 30) * weights["delivery_days"] +
                profiles["min_price_discount"]         * weights["price_discount"] +
                profiles["years_active"].clip(0, 20)  / 20 * weights["years_active"] +
                (profiles[comm_col] if comm_col in profiles.columns
                 else 0.5) * weights["commodity_match"]
            )
            # Region boost
            scores += (profiles["region"] == region).astype(float) * 0.10
            # Capacity filter
            scores -= (profiles["max_quantity_qt"] < qty_qt).astype(float) * 0.20

            profiles["match_probability"] = scores.clip(0, 1)
            top5 = profiles.nlargest(5, "match_probability")

            # Build result list that matches the shape callers expect
            results = []
            for _, row in top5.iterrows():
                results.append({
                    "id":                  row["merchant_id"],
                    "name":                row["merchant_id"],   # no real name in model
                    "phone":               None,
                    "region":              row["region"],
                    "preferred_sector":    "Agriculture",
                    "preferred_product":   commodity,
                    "max_budget_birr":     row["max_quantity_qt"] * price,
                    "avg_rating":          round(row["avg_rating"], 2),
                    "completion_rate":     round(row["completion_rate"] * 100, 1),
                    "avg_delivery_days":   round(row["avg_delivery_days"], 1),
                    "match_probability":   round(float(row["match_probability"]), 4),
                    "source":              "ml-model",
                })

            # Also score the live Supabase merchants and prepend them
            live = _score_live_merchants(listing_data, merchant_list)
            # Merge: live first (they have real contact info), model fills remainder
            seen_ids = {m["id"] for m in live}
            combined = live + [m for m in results if m["id"] not in seen_ids]
            return sorted(combined, key=lambda x: x["match_probability"], reverse=True)

        except Exception:
            pass

    # ── Fallback: score only the live Supabase list ──────────
    return _score_live_merchants(listing_data, merchant_list)


def _score_live_merchants(listing_data, merchant_list):
    """Rule-based scoring for live Supabase merchant records."""
    ranked = []
    for m in merchant_list:
        score = 0.5
        if m.get("preferred_sector") == listing_data.get("sector"):
            score += 0.20
        if m.get("region") == listing_data.get("region"):
            score += 0.15
        if m.get("max_budget_birr", 0) >= listing_data.get("price_birr", 0):
            score += 0.15
        ranked.append({
            "id":               m.get("id"),
            "name":             m.get("name", "Unknown"),
            "phone":            m.get("phone"),
            "region":           m.get("region"),
            "preferred_sector": m.get("preferred_sector"),
            "preferred_product":m.get("preferred_product"),
            "max_budget_birr":  m.get("max_budget_birr"),
            "match_probability":round(min(score, 1.0), 4),
            "source":           "rule-based",
        })
    return sorted(ranked, key=lambda x: x["match_probability"], reverse=True)
