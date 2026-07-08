"""
src/recommendation_engine.py — AI Product Recommendation Engine
Uses trained SVD + content-based hybrid model (recommendation_engine.pkl).
Call from any page that needs "Recommended for You" or "Similar Products".
"""
import os
import sys
import logging
from typing import Optional, Dict, Any, List, Union
import pandas as pd
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────────────────────
_rec_model = None
_MODEL_PATH = None

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
DEFAULT_TOP_K = 8
MAX_TOP_K = 20

# Default weights for recommendation scoring
DEFAULT_WEIGHTS = {
    "rating": 0.40,
    "popularity": 0.35,
    "certified": 0.15,
    "organic": 0.10,
}

# ─────────────────────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────────────────────

def get_model_path() -> Optional[str]:
    """
    Find the recommendation engine model file.
    
    Returns:
        Optional[str]: Path to model file or None if not found
    """
    global _MODEL_PATH
    
    if _MODEL_PATH is not None:
        return _MODEL_PATH
    
    # Search paths for model
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", "models", "recommendation_engine.pkl"),
        os.path.join(os.path.dirname(__file__), "recommendation_engine.pkl"),
        "recommendation_engine.pkl",
        "models/recommendation_engine.pkl",
        os.path.join(os.getcwd(), "models", "recommendation_engine.pkl"),
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            _MODEL_PATH = path
            logger.info(f"Found recommendation model at: {path}")
            return _MODEL_PATH
    
    logger.warning("Recommendation model file not found in any search path")
    return None

def _load_model() -> Optional[Dict[str, Any]]:
    """
    Load the recommendation engine model.
    
    Returns:
        Optional[Dict]: Model dictionary with 'product_df' and optionally 'user_matrix'
    """
    global _rec_model
    
    if _rec_model is not None:
        return _rec_model
    
    model_path = get_model_path()
    if model_path is None:
        return None
    
    try:
        import joblib
        _rec_model = joblib.load(model_path)
        logger.info("Recommendation model loaded successfully")
        
        # Ensure required keys exist
        if "product_df" not in _rec_model:
            logger.warning("Model missing 'product_df' key")
            _rec_model["product_df"] = pd.DataFrame()
        
        if _rec_model["product_df"] is None or _rec_model["product_df"].empty:
            logger.warning("Product DataFrame is empty")
            _rec_model["product_df"] = _create_default_product_df()
        
        return _rec_model
        
    except ImportError:
        logger.error("joblib not installed. Please install: pip install joblib")
        return None
    except Exception as e:
        logger.error(f"Failed to load recommendation model: {e}")
        return None

def _create_default_product_df() -> pd.DataFrame:
    """
    Create a default product DataFrame for when model is unavailable.
    
    Returns:
        pd.DataFrame: Default product data
    """
    return pd.DataFrame({
        "product_id": [],
        "commodity": [],
        "region": [],
        "price_etb": [],
        "avg_rating": [],
        "sales_count": [],
        "is_organic": [],
        "is_certified": [],
        "category": [],
    })

def load_recommendation_model() -> Optional[Dict[str, Any]]:
    """
    Public function to load the recommendation model.
    
    Returns:
        Optional[Dict]: Model dictionary or None if loading fails
    """
    return _load_model()

# ─────────────────────────────────────────────────────────────
# RECOMMENDATION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_recommendations(
    commodity: Optional[str] = None,
    region: Optional[str] = None,
    top_k: int = DEFAULT_TOP_K,
    user_id: Optional[str] = None,
    exclude_ids: Optional[List[str]] = None,
    category: Optional[str] = None,
    min_rating: float = 0.0,
    max_price: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Get product recommendations with optional filters.
    
    Args:
        commodity: Filter by commodity (e.g., "Teff", "Coffee")
        region: Filter by region
        top_k: Number of recommendations to return
        user_id: Optional user ID for personalized recommendations
        exclude_ids: List of product IDs to exclude
        category: Filter by category
        min_rating: Minimum rating threshold
        max_price: Maximum price threshold
    
    Returns:
        List[Dict]: Recommended products
    """
    # Validate inputs
    top_k = min(max(top_k, 1), MAX_TOP_K)  # Clamp between 1 and MAX_TOP_K
    
    model_data = _load_model()
    if model_data is None:
        logger.warning("Model not available, returning empty recommendations")
        return []
    
    try:
        products = model_data.get("product_df")
        if products is None or products.empty:
            logger.warning("No product data available")
            return []
        
        # Create a copy to avoid modifying original
        df = products.copy()
        
        # Apply filters
        mask = pd.Series([True] * len(df), index=df.index)
        
        if commodity:
            commodity_lower = commodity.lower().strip()
            if "commodity" in df.columns:
                mask &= df["commodity"].str.lower().str.contains(commodity_lower, na=False)
            else:
                logger.warning("'commodity' column not found in product data")
        
        if region:
            region_lower = region.lower().strip()
            if "region" in df.columns:
                mask &= df["region"].str.lower().str.contains(region_lower, na=False)
            else:
                logger.warning("'region' column not found in product data")
        
        if category:
            category_lower = category.lower().strip()
            if "category" in df.columns:
                mask &= df["category"].str.lower().str.contains(category_lower, na=False)
            else:
                logger.warning("'category' column not found in product data")
        
        if min_rating > 0:
            if "avg_rating" in df.columns:
                mask &= df["avg_rating"] >= min_rating
            else:
                logger.warning("'avg_rating' column not found in product data")
        
        if max_price is not None and max_price > 0:
            if "price_etb" in df.columns:
                mask &= df["price_etb"] <= max_price
            else:
                logger.warning("'price_etb' column not found in product data")
        
        if exclude_ids:
            if "product_id" in df.columns:
                mask &= ~df["product_id"].isin(exclude_ids)
            else:
                logger.warning("'product_id' column not found in product data")
        
        # Apply mask
        filtered = df[mask].copy() if mask.any() else df.copy()
        
        if filtered.empty:
            logger.info("No products match the filters")
            return []
        
        # Calculate scores
        filtered = _calculate_scores(filtered)
        
        # Get top N
        top = filtered.nlargest(top_k, "score")
        
        # Convert to list of dicts
        results = top.to_dict(orient="records")
        
        # Add human-readable labels
        for item in results:
            item["score_percent"] = round(item.get("score", 0) * 100, 1)
            
            # Add rating stars
            rating = item.get("avg_rating", 0)
            if rating > 0:
                stars = "★" * int(round(rating)) + "☆" * (5 - int(round(rating)))
                item["stars"] = stars
            else:
                item["stars"] = "☆☆☆☆☆"
            
            # Add price label
            price = item.get("price_etb", 0)
            item["price_label"] = f"ETB {price:,.2f}"
        
        logger.info(f"Returning {len(results)} recommendations")
        return results
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return []

def _calculate_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate recommendation scores for products.
    
    Args:
        df: Product DataFrame
    
    Returns:
        pd.DataFrame: DataFrame with 'score' column added
    """
    # Initialize score column
    df = df.copy()
    df["score"] = 0.0
    
    # 1. Rating score (40%)
    if "avg_rating" in df.columns:
        # Normalize rating to 0-1
        rating_max = 5.0
        rating_score = df["avg_rating"].fillna(0) / rating_max
        df["score"] += rating_score * DEFAULT_WEIGHTS["rating"]
    
    # 2. Popularity score (35%)
    if "sales_count" in df.columns:
        # Log-normalize sales count
        sales = df["sales_count"].fillna(0).clip(lower=0)
        max_sales = sales.max() if sales.max() > 0 else 1
        popularity_score = np.log1p(sales) / (np.log1p(max_sales) + 1e-9)
        df["score"] += popularity_score * DEFAULT_WEIGHTS["popularity"]
    
    # 3. Certified bonus (15%)
    if "is_certified" in df.columns:
        certified_score = df["is_certified"].fillna(0).astype(float)
        df["score"] += certified_score * DEFAULT_WEIGHTS["certified"]
    
    # 4. Organic bonus (10%)
    if "is_organic" in df.columns:
        organic_score = df["is_organic"].fillna(0).astype(float)
        df["score"] += organic_score * DEFAULT_WEIGHTS["organic"]
    
    # 5. Normalize to 0-1
    score_max = df["score"].max() if df["score"].max() > 0 else 1
    df["score"] = df["score"] / score_max
    
    return df

# ─────────────────────────────────────────────────────────────
# ENHANCED RECOMMENDATION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_similar_products(
    commodity: str,
    top_k: int = DEFAULT_TOP_K,
    region: Optional[str] = None,
    exclude_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get products similar to a given commodity.
    
    Args:
        commodity: Commodity name
        top_k: Number of recommendations
        region: Optional region filter
        exclude_id: Optional product ID to exclude
    
    Returns:
        List[Dict]: Similar products
    """
    exclude_ids = [exclude_id] if exclude_id else None
    return get_recommendations(
        commodity=commodity,
        region=region,
        top_k=top_k,
        exclude_ids=exclude_ids
    )

def get_personalized_recommendations(
    user_id: str,
    top_k: int = DEFAULT_TOP_K,
    region: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Get personalized recommendations for a user.
    
    Args:
        user_id: User ID
        top_k: Number of recommendations
        region: Optional region filter
        preferences: User preferences dict
    
    Returns:
        List[Dict]: Personalized recommendations
    """
    # This would typically use a user-specific model
    # For now, use content-based with user preferences
    commodity = preferences.get("preferred_commodity") if preferences else None
    category = preferences.get("preferred_category") if preferences else None
    
    return get_recommendations(
        commodity=commodity,
        region=region,
        category=category,
        top_k=top_k,
        user_id=user_id
    )

def get_popular_products(
    top_k: int = DEFAULT_TOP_K,
    region: Optional[str] = None,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get most popular products.
    
    Args:
        top_k: Number of products
        region: Optional region filter
        category: Optional category filter
    
    Returns:
        List[Dict]: Popular products
    """
    model_data = _load_model()
    if model_data is None:
        return []
    
    try:
        df = model_data.get("product_df")
        if df is None or df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df), index=df.index)
        
        if region:
            region_lower = region.lower().strip()
            if "region" in df.columns:
                mask &= df["region"].str.lower().str.contains(region_lower, na=False)
        
        if category:
            category_lower = category.lower().strip()
            if "category" in df.columns:
                mask &= df["category"].str.lower().str.contains(category_lower, na=False)
        
        filtered = df[mask].copy() if mask.any() else df.copy()
        
        if filtered.empty:
            return []
        
        # Sort by sales_count
        if "sales_count" in filtered.columns:
            sorted_df = filtered.sort_values("sales_count", ascending=False)
        elif "avg_rating" in filtered.columns:
            sorted_df = filtered.sort_values("avg_rating", ascending=False)
        else:
            sorted_df = filtered
        
        top = sorted_df.head(top_k)
        
        results = top.to_dict(orient="records")
        
        # Add labels
        for item in results:
            item["score_percent"] = 100
            rating = item.get("avg_rating", 0)
            if rating > 0:
                stars = "★" * int(round(rating)) + "☆" * (5 - int(round(rating)))
                item["stars"] = stars
            else:
                item["stars"] = "☆☆☆☆☆"
            price = item.get("price_etb", 0)
            item["price_label"] = f"ETB {price:,.2f}"
            item["is_popular"] = True
        
        return results
        
    except Exception as e:
        logger.error(f"Popular products error: {e}")
        return []

def get_top_rated_products(
    top_k: int = DEFAULT_TOP_K,
    region: Optional[str] = None,
    min_rating: float = 4.0,
    min_reviews: int = 5
) -> List[Dict[str, Any]]:
    """
    Get top-rated products.
    
    Args:
        top_k: Number of products
        region: Optional region filter
        min_rating: Minimum rating threshold
        min_reviews: Minimum number of reviews
    
    Returns:
        List[Dict]: Top-rated products
    """
    model_data = _load_model()
    if model_data is None:
        return []
    
    try:
        df = model_data.get("product_df")
        if df is None or df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df), index=df.index)
        
        if region:
            region_lower = region.lower().strip()
            if "region" in df.columns:
                mask &= df["region"].str.lower().str.contains(region_lower, na=False)
        
        if min_rating > 0 and "avg_rating" in df.columns:
            mask &= df["avg_rating"] >= min_rating
        
        if min_reviews > 0 and "review_count" in df.columns:
            mask &= df["review_count"] >= min_reviews
        
        filtered = df[mask].copy() if mask.any() else df.copy()
        
        if filtered.empty:
            return []
        
        # Sort by rating
        if "avg_rating" in filtered.columns:
            sorted_df = filtered.sort_values("avg_rating", ascending=False)
        else:
            sorted_df = filtered
        
        top = sorted_df.head(top_k)
        
        results = top.to_dict(orient="records")
        
        # Add labels
        for item in results:
            rating = item.get("avg_rating", 0)
            if rating > 0:
                stars = "★" * int(round(rating)) + "☆" * (5 - int(round(rating)))
                item["stars"] = stars
            else:
                item["stars"] = "☆☆☆☆☆"
            price = item.get("price_etb", 0)
            item["price_label"] = f"ETB {price:,.2f}"
            item["is_top_rated"] = True
        
        return results
        
    except Exception as e:
        logger.error(f"Top rated products error: {e}")
        return []

def get_category_recommendations(
    category: str,
    top_k: int = DEFAULT_TOP_K,
    region: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get recommendations by category.
    
    Args:
        category: Category name
        top_k: Number of products
        region: Optional region filter
    
    Returns:
        List[Dict]: Category recommendations
    """
    return get_recommendations(
        category=category,
        region=region,
        top_k=top_k
    )

def get_region_recommendations(
    region: str,
    top_k: int = DEFAULT_TOP_K,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get recommendations by region.
    
    Args:
        region: Region name
        top_k: Number of products
        category: Optional category filter
    
    Returns:
        List[Dict]: Region recommendations
    """
    return get_recommendations(
        region=region,
        category=category,
        top_k=top_k
    )

def get_hybrid_recommendations(
    user_id: Optional[str] = None,
    commodity: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = DEFAULT_TOP_K,
    mix_ratio: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Get hybrid recommendations combining multiple strategies.
    
    Args:
        user_id: Optional user ID
        commodity: Preferred commodity
        region: Preferred region
        category: Preferred category
        top_k: Number of recommendations
        mix_ratio: Ratio of content-based vs collaborative (0-1)
    
    Returns:
        List[Dict]: Hybrid recommendations
    """
    # Get content-based recommendations
    content_recs = get_recommendations(
        commodity=commodity,
        region=region,
        category=category,
        top_k=top_k * 2
    )
    
    # Get collaborative recommendations
    collab_recs = []
    if user_id:
        collab_recs = get_personalized_recommendations(user_id, top_k=top_k * 2)
    
    # Combine and deduplicate
    combined = []
    seen_ids = set()
    
    # Add collaborative first (higher weight)
    for item in collab_recs:
        item_id = item.get("product_id")
        if item_id and item_id not in seen_ids:
            item["score"] = item.get("score", 0.5) + 0.2
            combined.append(item)
            seen_ids.add(item_id)
    
    # Add content-based
    for item in content_recs:
        item_id = item.get("product_id")
        if item_id and item_id not in seen_ids:
            item["score"] = item.get("score", 0.5)
            combined.append(item)
            seen_ids.add(item_id)
    
    # Sort by score
    combined.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return combined[:top_k]

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Recommendation Engine")
    print("=" * 50)
    
    # Test recommendations
    print("\n📊 Test 1: Recommendations for Teff in Oromia")
    recs = get_recommendations(commodity="Teff", region="Oromia", top_k=5)
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec.get('commodity', 'Unknown')} - ETB {rec.get('price_etb', 0):.2f}")
        print(f"     Rating: {rec.get('avg_rating', 0):.1f}★, Score: {rec.get('score_percent', 0):.1f}%")
    
    # Test similar products
    print("\n📊 Test 2: Similar to Coffee")
    similar = get_similar_products("Coffee", top_k=5)
    for i, item in enumerate(similar, 1):
        print(f"  {i}. {item.get('commodity', 'Unknown')} - ETB {item.get('price_etb', 0):.2f}")
    
    # Test popular products
    print("\n📊 Test 3: Popular Products")
    popular = get_popular_products(top_k=5)
    for i, item in enumerate(popular, 1):
        print(f"  {i}. {item.get('commodity', 'Unknown')} - Sales: {item.get('sales_count', 0)}")
    
    # Test top rated
    print("\n📊 Test 4: Top Rated Products")
    top_rated = get_top_rated_products(top_k=5)
    for i, item in enumerate(top_rated, 1):
        print(f"  {i}. {item.get('commodity', 'Unknown')} - {item.get('avg_rating', 0):.1f}★")
