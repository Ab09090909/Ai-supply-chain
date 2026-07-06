"""
src/matching_engine.py — AI Merchant Matching Engine
"""

def rank_merchants(listing_data, merchant_list):
    """
    Ranks merchants based on compatibility with a product listing.
    """
    ranked = []
    for m in merchant_list:
        score = 0.5  # Base score
        
        # Sector match
        if m.get("preferred_sector") == listing_data.get("sector"):
            score += 0.2
            
        # Region proximity
        if m.get("region") == listing_data.get("region"):
            score += 0.15
            
        # Budget fit
        if m.get("max_budget_birr", 0) >= listing_data.get("price_birr", 0):
            score += 0.15
            
        ranked.append({
            "id": m["id"],
            "name": m.get("name", "Unknown"),
            "phone": m.get("phone"),
            "region": m.get("region"),
            "preferred_sector": m.get("preferred_sector"),
            "preferred_product": m.get("preferred_product"),
            "max_budget_birr": m.get("max_budget_birr"),
            "match_probability": min(score, 1.0)
        })
        
    # Sort by highest probability
    return sorted(ranked, key=lambda x: x["match_probability"], reverse=True)
