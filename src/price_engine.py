"""
src/price_engine.py — AI Price Recommendation Engine
"""

def recommend_price(sector, product, region, quality_grade, quantity):
    """
    Recommends a fair market price.
    """
    base_prices = {
        'Agriculture': 150, 'Livestock': 2500, 'Handicrafts': 300,
        'Manufacturing': 400, 'Food Processing': 250, 'Textiles': 350, 'Services': 200
    }
    base = base_prices.get(sector, 200)
    
    # Adjust for quality grade
    grade_multiplier = {'A': 1.3, 'B': 1.0, 'C': 0.7}.get(quality_grade, 1.0)
    
    return {
        "recommended_price_birr": base * grade_multiplier,
        "confidence": 0.6,
        "method": "rule-based-fallback"
    }
