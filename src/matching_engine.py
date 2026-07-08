"""
src/matching_engine.py — AI Merchant Matching Engine
Uses trained cosine-similarity model (merchant_matcher.pkl).
Falls back to rule-based scoring if model unavailable.
"""
import os
import sys
import logging
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────────────────────
_match_model = None
_MODEL_PATH = None

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
# Commodity mapping for product name → standardized commodity
_COMMODITY_MAP = {
    # Grains
    "teff": "Teff",
    "maize": "Maize",
    "corn": "Maize",
    "wheat": "Wheat",
    "sorghum": "Sorghum",
    "barley": "Barley",
    "millet": "Millet",
    "rice": "Rice",
    # Pulses
    "lentils": "Lentils",
    "chickpeas": "Chickpeas",
    "haricot beans": "Haricot Beans",
    "faba beans": "Faba Beans",
    "field peas": "Field Peas",
    # Oilseeds
    "sesame": "Sesame",
    "sunflower": "Sunflower",
    "niger seed": "Niger Seed",
    "groundnut": "Groundnut",
    "soybean": "Soybean",
    # Cash crops
    "coffee": "Coffee",
    "chat": "Chat",
    "cotton": "Cotton",
    "sugarcane": "Sugarcane",
    # Vegetables
    "potato": "Potato",
    "onion": "Onion",
    "tomato": "Tomato",
    "cabbage": "Cabbage",
    "carrot": "Carrot",
    "garlic": "Garlic",
    # Fruits
    "banana": "Banana",
    "mango": "Mango",
    "papaya": "Papaya",
    "avocado": "Avocado",
    "citrus": "Citrus",
    # Livestock products
    "milk": "Milk",
    "meat": "Meat",
    "egg": "Egg",
    "honey": "Honey",
}

# Region mapping for standardized region names
_REGION_MAP = {
    "addis ababa": "Addis Ababa",
    "oromia": "Oromia",
    "amhara": "Amhara",
    "tigray": "Tigray",
    "afar": "Afar",
    "somali": "Somali",
    "sidama": "Sidama",
    "snnp": "SNNP",
    "snnpr": "SNNP",
    "gambela": "Gambela",
    "harari": "Harari",
    "dire dawa": "Dire Dawa",
    "benishangul-gumuz": "Benishangul-Gumuz",
    "south west": "South West",
    "central ethiopia": "Central Ethiopia",
    "south ethiopia": "South Ethiopia",
}

# Default weights for scoring
DEFAULT_WEIGHTS = {
    "rating": 0.25,
    "completion_rate": 0.20,
    "delivery_days": 0.15,
    "price_discount": 0.15,
    "years_active": 0.10,
    "commodity_match": 0.15,
}

# ─────────────────────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────────────────────

def get_model_path() -> Optional[str]:
    """
    Find the merchant matcher model file.
    
    Returns:
        Optional[str]: Path to model file or None if not found
    """
    global _MODEL_PATH
    
    if _MODEL_PATH is not None:
        return _MODEL_PATH
    
    # Search paths for model
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", "models", "merchant_matcher.pkl"),
        os.path.join(os.path.dirname(__file__), "merchant_matcher.pkl"),
        "merchant_matcher.pkl",
        "models/merchant_matcher.pkl",
        os.path.join(os.getcwd(), "models", "merchant_matcher.pkl"),
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            _MODEL_PATH = path
            logger.info(f"Found matching model at: {path}")
            return _MODEL_PATH
    
    logger.warning("Matching model file not found in any search path")
    return None

def _load_model() -> Optional[Dict[str, Any]]:
    """
    Load the merchant matching model.
    
    Returns:
        Optional[Dict]: Model dictionary with 'merchant_profiles' and 'weights'
    """
    global _match_model
    
    if _match_model is not None:
        return _match_model
    
    model_path = get_model_path()
    if model_path is None:
        return None
    
    try:
        import joblib
        _match_model = joblib.load(model_path)
        logger.info("Matching model loaded successfully")
        
        # Ensure required keys exist
        if "merchant_profiles" not in _match_model:
            logger.warning("Model missing 'merchant_profiles'")
            _match_model["merchant_profiles"] = pd.DataFrame()
        
        if "weights" not in _match_model:
            _match_model["weights"] = DEFAULT_WEIGHTS
            logger.info("Using default weights")
        
        return _match_model
        
    except ImportError:
        logger.error("joblib not installed. Please install: pip install joblib")
        return None
    except Exception as e:
        logger.error(f"Failed to load matching model: {e}")
        return None

def load_matching_model() -> Optional[Dict[str, Any]]:
    """
    Public function to load the matching model.
    
    Returns:
        Optional[Dict]: Model dictionary or None if loading fails
    """
    return _load_model()

# ─────────────────────────────────────────────────────────────
# MATCHING FUNCTIONS
# ─────────────────────────────────────────────────────────────

def rank_merchants(
    listing_data: Dict[str, Any],
    merchant_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Rank merchants by match probability for a listing.
    
    Args:
        listing_data: Product listing with keys: sector, product, region, price_birr, quantity
        merchant_list: List of merchant dictionaries from Supabase
    
    Returns:
        List[Dict]: Ranked merchants with match_probability
    """
    # Validate inputs
    if not merchant_list:
        logger.warning("No merchants provided for ranking")
        return []
    
    if not listing_data:
        logger.warning("No listing data provided")
        return []
    
    try:
        # Try ML-based matching
        model = _load_model()
        if model is not None:
            ml_result = _ml_ranking(listing_data, merchant_list, model)
            if ml_result is not None:
                return ml_result
    except Exception as e:
        logger.error(f"ML ranking failed: {e}")
    
    # Fallback to rule-based matching
    logger.info("Using rule-based merchant matching")
    return _rule_based_ranking(listing_data, merchant_list)

def _ml_ranking(
    listing_data: Dict[str, Any],
    merchant_list: List[Dict[str, Any]],
    model: Dict[str, Any]
) -> Optional[List[Dict[str, Any]]]:
    """
    Rank merchants using ML model.
    
    Returns:
        Optional[List[Dict]]: Ranked merchants or None if ML fails
    """
    try:
        import pandas as pd
        
        # Get model components
        profiles = model.get("merchant_profiles")
        weights = model.get("weights", DEFAULT_WEIGHTS)
        
        if profiles is None or profiles.empty:
            logger.warning("Merchant profiles not available")
            return None
        
        # Prepare listing features
        comm_key = str(listing_data.get("product", "")).lower().strip()
        commodity = _COMMODITY_MAP.get(comm_key, "Teff")
        comm_col = f"spec_{commodity.lower().replace(' ', '_')}"
        
        reg_key = str(listing_data.get("region", "")).lower().strip()
        region = _REGION_MAP.get(reg_key, "Oromia")
        
        qty_qt = float(listing_data.get("quantity", 100))
        price = float(listing_data.get("price_birr", 0))
        
        # Calculate scores
        scores = (
            profiles.get("avg_rating", 3.5) / 5.0 * weights.get("rating", 0.25) +
            profiles.get("completion_rate", 0.8) * weights.get("completion_rate", 0.20) +
            (1 - profiles.get("avg_delivery_days", 15).clip(0, 30) / 30) * weights.get("delivery_days", 0.15) +
            profiles.get("min_price_discount", 0.1) * weights.get("price_discount", 0.15) +
            profiles.get("years_active", 1).clip(0, 20) / 20 * weights.get("years_active", 0.10)
        )
        
        # Commodity match
        if comm_col in profiles.columns:
            scores += profiles[comm_col] * weights.get("commodity_match", 0.15)
        else:
            scores += 0.5 * weights.get("commodity_match", 0.15)
        
        # Region boost
        region_col = profiles.get("region", "")
        scores += (region_col == region).astype(float) * 0.10
        
        # Capacity filter
        max_qty = profiles.get("max_quantity_qt", 0)
        scores -= (max_qty < qty_qt).astype(float) * 0.20
        
        # Clip scores
        scores = scores.clip(0, 1)
        
        # Create results
        results = []
        profiles_copy = profiles.copy()
        profiles_copy["match_probability"] = scores
        
        # Get top merchants
        top_n = min(10, len(profiles_copy))
        top_merchants = profiles_copy.nlargest(top_n, "match_probability")
        
        for _, row in top_merchants.iterrows():
            merchant_id = row.get("merchant_id", row.get("id", ""))
            
            # Find matching merchant from live list for additional info
            live_merchant = next(
                (m for m in merchant_list if str(m.get("id")) == str(merchant_id)),
                {}
            )
            
            results.append({
                "id": merchant_id,
                "name": live_merchant.get("name", row.get("merchant_id", "Unknown")),
                "phone": live_merchant.get("phone"),
                "email": live_merchant.get("email"),
                "region": row.get("region", region),
                "preferred_sector": row.get("preferred_sector", listing_data.get("sector", "Agriculture")),
                "preferred_product": row.get("preferred_product", commodity),
                "max_budget_birr": row.get("max_quantity_qt", 0) * price,
                "avg_rating": round(row.get("avg_rating", 0), 2),
                "completion_rate": round(row.get("completion_rate", 0) * 100, 1),
                "avg_delivery_days": round(row.get("avg_delivery_days", 0), 1),
                "years_active": round(row.get("years_active", 0), 1),
                "match_probability": round(float(row.get("match_probability", 0)), 4),
                "source": "ml-model",
                "is_verified": live_merchant.get("is_verified", False),
            })
        
        # Also include live merchants with high scores
        live_results = _rule_based_ranking(listing_data, merchant_list)
        
        # Merge: live first (they have real contact info), model fills remainder
        seen_ids = {str(m.get("id")) for m in live_results if m.get("id")}
        combined = live_results[:3]  # Keep top 3 live merchants
        
        # Add ML merchants not already in live results
        for m in results:
            if str(m.get("id")) not in seen_ids:
                combined.append(m)
        
        return sorted(combined, key=lambda x: x.get("match_probability", 0), reverse=True)
        
    except Exception as e:
        logger.error(f"ML ranking error: {e}")
        return None

def _rule_based_ranking(
    listing_data: Dict[str, Any],
    merchant_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Rank merchants using rule-based scoring.
    
    Args:
        listing_data: Product listing data
        merchant_list: List of merchants
    
    Returns:
        List[Dict]: Ranked merchants
    """
    ranked = []
    
    sector = listing_data.get("sector", "")
    region = listing_data.get("region", "")
    price = float(listing_data.get("price_birr", 0))
    quantity = float(listing_data.get("quantity", 0))
    product = listing_data.get("product", "")
    
    for m in merchant_list:
        score = 0.5  # Base score
        
        # Preferred sector match (25% weight)
        if m.get("preferred_sector") == sector:
            score += 0.25
        
        # Region match (20% weight)
        if m.get("region") == region:
            score += 0.20
        
        # Budget match (15% weight)
        max_budget = m.get("max_budget_birr", 0)
        if max_budget >= price:
            score += 0.15
        elif max_budget > 0:
            score += 0.05  # Partial match
        
        # Preferred product match (15% weight)
        pref_product = m.get("preferred_product", "")
        if pref_product and product:
            if pref_product.lower() == product.lower():
                score += 0.15
            elif any(p in product.lower() for p in pref_product.lower().split()):
                score += 0.08
        
        # Rating bonus (10% weight)
        rating = m.get("avg_rating", 0)
        if rating >= 4.5:
            score += 0.10
        elif rating >= 4.0:
            score += 0.05
        
        # Verification bonus (10% weight)
        if m.get("is_verified", False):
            score += 0.10
        
        # Completion rate bonus (5% weight)
        completion = m.get("completion_rate", 0)
        if completion >= 90:
            score += 0.05
        elif completion >= 80:
            score += 0.03
        
        # Cap score
        score = min(score, 1.0)
        
        ranked.append({
            "id": m.get("id"),
            "name": m.get("name", "Unknown"),
            "phone": m.get("phone"),
            "email": m.get("email"),
            "region": m.get("region"),
            "preferred_sector": m.get("preferred_sector"),
            "preferred_product": m.get("preferred_product"),
            "max_budget_birr": m.get("max_budget_birr"),
            "avg_rating": m.get("avg_rating", 0),
            "completion_rate": m.get("completion_rate", 0),
            "avg_delivery_days": m.get("avg_delivery_days", 0),
            "years_active": m.get("years_active", 0),
            "match_probability": round(score, 4),
            "source": "rule-based",
            "is_verified": m.get("is_verified", False),
        })
    
    return sorted(ranked, key=lambda x: x.get("match_probability", 0), reverse=True)

# ─────────────────────────────────────────────────────────────
# ENHANCED MATCHING FUNCTIONS
# ─────────────────────────────────────────────────────────────

def find_best_match(
    listing_data: Dict[str, Any],
    merchant_list: List[Dict[str, Any]],
    min_score: float = 0.6
) -> Optional[Dict[str, Any]]:
    """
    Find the best matching merchant for a listing.
    
    Args:
        listing_data: Product listing data
        merchant_list: List of merchants
        min_score: Minimum match probability threshold
    
    Returns:
        Optional[Dict]: Best matching merchant or None
    """
    ranked = rank_merchants(listing_data, merchant_list)
    
    # Filter by minimum score
    filtered = [m for m in ranked if m.get("match_probability", 0) >= min_score]
    
    if filtered:
        return filtered[0]
    
    # Return best if any exists
    if ranked:
        return ranked[0]
    
    return None

def get_top_merchants(
    listing_data: Dict[str, Any],
    merchant_list: List[Dict[str, Any]],
    n: int = 5,
    min_score: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Get top N matching merchants.
    
    Args:
        listing_data: Product listing data
        merchant_list: List of merchants
        n: Number of merchants to return
        min_score: Minimum match probability threshold
    
    Returns:
        List[Dict]: Top N merchants
    """
    ranked = rank_merchants(listing_data, merchant_list)
    
    # Filter by minimum score
    filtered = [m for m in ranked if m.get("match_probability", 0) >= min_score]
    
    return filtered[:n]

def get_match_summary(
    listing_data: Dict[str, Any],
    merchant_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Get summary of matching results.
    
    Args:
        listing_data: Product listing data
        merchant_list: List of merchants
    
    Returns:
        Dict: Match summary
    """
    ranked = rank_merchants(listing_data, merchant_list)
    
    if not ranked:
        return {
            "total_merchants": 0,
            "best_match": None,
            "top_5": [],
            "average_score": 0,
            "distribution": {"high": 0, "medium": 0, "low": 0}
        }
    
    # Calculate distribution
    high_count = sum(1 for m in ranked if m.get("match_probability", 0) >= 0.7)
    medium_count = sum(1 for m in ranked if 0.4 <= m.get("match_probability", 0) < 0.7)
    low_count = sum(1 for m in ranked if m.get("match_probability", 0) < 0.4)
    
    return {
        "total_merchants": len(ranked),
        "best_match": ranked[0] if ranked else None,
        "top_5": ranked[:5],
        "average_score": round(np.mean([m.get("match_probability", 0) for m in ranked]), 4),
        "distribution": {
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        },
        "listing": {
            "product": listing_data.get("product", ""),
            "sector": listing_data.get("sector", ""),
            "region": listing_data.get("region", ""),
            "price": listing_data.get("price_birr", 0),
            "quantity": listing_data.get("quantity", 0)
        }
    }

def get_match_breakdown(match_result: Dict[str, Any]) -> Dict[str, float]:
    """
    Get detailed breakdown of match factors.
    
    Args:
        match_result: Match result from ranking
    
    Returns:
        Dict: Breakdown of match factors
    """
    breakdown = {
        "sector_match": 0.0,
        "region_match": 0.0,
        "budget_match": 0.0,
        "rating_match": 0.0,
        "verification": 0.0,
        "completion_rate": 0.0
    }
    
    # This is a placeholder for detailed breakdown
    # Would need more data to calculate accurately
    
    return breakdown

# ─────────────────────────────────────────────────────────────
# DATA PREPARATION HELPERS
# ─────────────────────────────────────────────────────────────

def prepare_merchant_profiles(
    merchant_list: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Prepare merchant profiles for ML matching.
    
    Args:
        merchant_list: List of merchants from database
    
    Returns:
        pd.DataFrame: Prepared merchant profiles
    """
    if not merchant_list:
        return pd.DataFrame()
    
    try:
        profiles = []
        for m in merchant_list:
            profile = {
                "merchant_id": m.get("id"),
                "region": m.get("region", ""),
                "preferred_sector": m.get("preferred_sector", ""),
                "preferred_product": m.get("preferred_product", ""),
                "max_budget_birr": float(m.get("max_budget_birr", 0)),
                "avg_rating": float(m.get("avg_rating", 3.5)),
                "completion_rate": float(m.get("completion_rate", 0.8)),
                "avg_delivery_days": float(m.get("avg_delivery_days", 15)),
                "years_active": float(m.get("years_active", 1)),
                "is_verified": int(m.get("is_verified", False)),
            }
            profiles.append(profile)
        
        return pd.DataFrame(profiles)
        
    except Exception as e:
        logger.error(f"Profile preparation error: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Merchant Matching Engine")
    print("=" * 50)
    
    # Sample listing
    listing = {
        "sector": "Agriculture",
        "product": "Teff",
        "region": "Oromia",
        "price_birr": 5000,
        "quantity": 10
    }
    
    # Sample merchants
    merchants = [
        {
            "id": "merchant_1",
            "name": "Abebe Trading",
            "phone": "+251-911-111-111",
            "region": "Oromia",
            "preferred_sector": "Agriculture",
            "preferred_product": "Teff",
            "max_budget_birr": 100000,
            "avg_rating": 4.5,
            "completion_rate": 95,
            "avg_delivery_days": 5,
            "years_active": 3,
            "is_verified": True
        },
        {
            "id": "merchant_2",
            "name": "Bekele Enterprises",
            "phone": "+251-922-222-222",
            "region": "Addis Ababa",
            "preferred_sector": "Agriculture",
            "preferred_product": "Wheat",
            "max_budget_birr": 50000,
            "avg_rating": 3.8,
            "completion_rate": 85,
            "avg_delivery_days": 8,
            "years_active": 2,
            "is_verified": False
        },
        {
            "id": "merchant_3",
            "name": "Chala Imports",
            "phone": "+251-933-333-333",
            "region": "Oromia",
            "preferred_sector": "Agriculture",
            "preferred_product": "Coffee",
            "max_budget_birr": 200000,
            "avg_rating": 4.8,
            "completion_rate": 98,
            "avg_delivery_days": 3,
            "years_active": 5,
            "is_verified": True
        }
    ]
    
    print(f"\n📋 Listing: {listing['product']} in {listing['region']}")
    
    # Get ranking
    ranked = rank_merchants(listing, merchants)
    
    print(f"\n📊 Top {len(ranked)} Merchants:")
    for i, m in enumerate(ranked, 1):
        print(f"  {i}. {m['name']} - {m['match_probability']:.2%} match")
        print(f"     Region: {m['region']} | Rating: {m.get('avg_rating', 0)}")
        print(f"     Source: {m.get('source', 'unknown')}")
    
    # Get best match
    best = find_best_match(listing, merchants)
    if best:
        print(f"\n🏆 Best Match: {best['name']} ({best['match_probability']:.2%})")
    
    # Get summary
    summary = get_match_summary(listing, merchants)
    print(f"\n📈 Summary:")
    print(f"  Total Merchants: {summary['total_merchants']}")
    print(f"  Average Score: {summary['average_score']:.2%}")
    print(f"  Distribution: High={summary['distribution']['high']}, Medium={summary['distribution']['medium']}, Low={summary['distribution']['low']}")
