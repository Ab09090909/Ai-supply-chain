"""
src/demand_engine.py — AI Demand Forecasting Engine
Returns a list of weekly demand values (what the producer page expects).
"""
import os
import sys
import logging
import datetime
from typing import Optional, List, Dict, Any, Union
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────────────────────
_demand_model = None
_MODEL_PATH = None

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
    # Sector-level fallbacks
    "agriculture": "Teff",
    "livestock": "Maize",
    "food processing": "Wheat",
    "manufacturing": "Barley",
    "handicrafts": "Sesame",
    "textiles": "Cotton",
    "services": "Coffee",
    "other": "Teff",
}

# Ethiopian holidays that affect demand (weeks)
_HOLIDAY_WEEKS = {
    9: 1.35,   # Fasika (Easter) - week 9
    10: 1.30,  # Fasika week
    11: 1.25,  # Post-Fasika
    35: 1.40,  # Meskel (September) - week 35
    36: 1.35,  # Meskel week
    37: 1.25,  # Post-Meskel
    50: 1.20,  # Christmas/Genna - week 50
    51: 1.15,  # Post-Christmas
    52: 1.20,  # New Year
    1: 1.15,   # New Year week
}

# Harvest seasons (weeks when supply is high → demand price lower)
_HARVEST_WEEKS = list(range(40, 53)) + list(range(1, 6))

# Base weekly demand (quintals) by sector
_SECTOR_BASE = {
    "Agriculture": 450,
    "Livestock": 80,
    "Food Processing": 200,
    "Manufacturing": 150,
    "Handicrafts": 60,
    "Textiles": 120,
    "Services": 50,
    "Technology": 30,
    "Construction": 100,
    "Transportation": 75,
    "Energy": 40,
    "Mining": 25,
    "Tourism": 35,
    "Education": 20,
    "Healthcare": 45,
    "Other": 100,
}

# Regional demand multipliers
_REGION_MULTIPLIERS = {
    "Addis Ababa": 1.50,
    "Oromia": 1.30,
    "Amhara": 1.20,
    "Tigray": 1.10,
    "Sidama": 1.15,
    "Somali": 0.90,
    "Afar": 0.85,
    "Benishangul-Gumuz": 0.80,
    "Gambela": 0.75,
    "Harari": 0.95,
    "Dire Dawa": 1.00,
    "South West": 1.05,
    "Central Ethiopia": 1.10,
    "South Ethiopia": 1.05,
}

# ─────────────────────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────────────────────

def get_model_path() -> Optional[str]:
    """
    Find the demand forecaster model file.
    
    Returns:
        Optional[str]: Path to model file or None if not found
    """
    global _MODEL_PATH
    
    if _MODEL_PATH is not None:
        return _MODEL_PATH
    
    # Search paths for model
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", "models", "demand_forecaster.pkl"),
        os.path.join(os.path.dirname(__file__), "demand_forecaster.pkl"),
        "demand_forecaster.pkl",
        "models/demand_forecaster.pkl",
        os.path.join(os.getcwd(), "models", "demand_forecaster.pkl"),
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            _MODEL_PATH = path
            logger.info(f"Found demand model at: {path}")
            return _MODEL_PATH
    
    logger.warning("Demand model file not found in any search path")
    return None

def _load_model() -> Optional[Dict[str, Any]]:
    """
    Load the demand forecasting model.
    
    Returns:
        Optional[Dict]: Model dictionary with 'model' and 'label_encoder' keys
    """
    global _demand_model
    
    if _demand_model is not None:
        return _demand_model
    
    model_path = get_model_path()
    if model_path is None:
        return None
    
    try:
        import joblib
        _demand_model = joblib.load(model_path)
        logger.info("Demand model loaded successfully")
        return _demand_model
    except ImportError:
        logger.error("joblib not installed. Please install: pip install joblib")
        return None
    except Exception as e:
        logger.error(f"Failed to load demand model: {e}")
        return None

def load_demand_model() -> Optional[Dict[str, Any]]:
    """
    Public function to load the demand model.
    
    Returns:
        Optional[Dict]: Model dictionary or None if loading fails
    """
    return _load_model()

# ─────────────────────────────────────────────────────────────
# FORECASTING FUNCTIONS
# ─────────────────────────────────────────────────────────────

def forecast_demand(
    sector: str = "Agriculture",
    product: Optional[str] = None,
    region: str = "Oromia",
    historical_data: Optional[List[float]] = None,
    horizon: int = 12,
    use_ml: bool = True
) -> List[float]:
    """
    Generate weekly demand forecasts.
    
    Args:
        sector: Sector name (Agriculture, Livestock, etc.)
        product: Product name (optional, overrides sector for commodity)
        region: Region name (affects demand multiplier)
        historical_data: List of historical demand values (optional)
        horizon: Number of weeks to forecast
        use_ml: Whether to use ML model if available
    
    Returns:
        List[float]: Weekly demand forecast values
    """
    if horizon <= 0:
        logger.warning(f"Invalid horizon: {horizon}, using default 12")
        horizon = 12
    
    # Ensure sector is properly formatted
    sector = sector.capitalize() if sector else "Agriculture"
    
    # Try ML-based forecast
    if use_ml:
        ml_result = _ml_forecast(
            sector=sector,
            product=product,
            region=region,
            historical_data=historical_data,
            horizon=horizon
        )
        if ml_result is not None:
            return ml_result
    
    # Fallback to rule-based forecast
    logger.info(f"Using rule-based forecast for {sector}")
    return _rule_based_forecast(
        sector=sector,
        region=region,
        horizon=horizon
    )

def _ml_forecast(
    sector: str,
    product: Optional[str],
    region: str,
    historical_data: Optional[List[float]],
    horizon: int
) -> Optional[List[float]]:
    """
    Generate forecast using ML model.
    
    Returns:
        Optional[List[float]]: Forecast values or None if ML fails
    """
    model_data = _load_model()
    if model_data is None:
        return None
    
    try:
        import pandas as pd
        from sklearn.preprocessing import LabelEncoder
        
        # Get model and encoder
        model = model_data.get("model")
        le = model_data.get("label_encoder")
        
        if model is None or le is None:
            logger.warning("Model or label encoder missing from model data")
            return None
        
        # Determine commodity
        commodity = _get_commodity(product, sector)
        
        # Encode commodity
        if commodity not in le.classes_:
            # If commodity not in training, use first class
            commodity = le.classes_[0]
            logger.debug(f"Using fallback commodity: {commodity}")
        
        commodity_encoded = int(le.transform([commodity])[0])
        
        # Get base demand from historical or default
        base_demand = _get_base_demand(historical_data, sector)
        
        # Generate forecasts
        now = datetime.datetime.now()
        forecasts = []
        lag1 = base_demand
        lag4 = base_demand
        ma4 = base_demand
        
        for i in range(horizon):
            future_date = now + datetime.timedelta(weeks=i + 1)
            woy = future_date.isocalendar()[1]
            month = future_date.month
            year = future_date.year
            
            # Prepare features
            features = pd.DataFrame([{
                "commodity_enc": commodity_encoded,
                "week": woy % 52 or 52,
                "month": month,
                "year": year,
                "week_of_year": woy,
                "is_holiday_week": int(woy in _HOLIDAY_WEEKS),
                "is_harvest_season": int(woy in _HARVEST_WEEKS),
                "rainfall_lag1": 55.0,  # Default rainfall
                "price_lag1": 3000.0,   # Default price
                "demand_lag1": lag1,
                "demand_lag4": lag4,
                "demand_ma4": ma4,
            }])
            
            # Predict
            pred = float(model.predict(features)[0])
            pred = max(0.0, pred)  # No negative demand
            
            # Apply regional multiplier
            region_mult = _REGION_MULTIPLIERS.get(region, 1.0)
            pred = pred * region_mult
            
            forecasts.append(round(pred, 1))
            
            # Update lags for next iteration
            lag4 = lag1
            lag1 = pred
            ma4 = float(np.mean(forecasts[-4:])) if len(forecasts) >= 4 else pred
        
        return forecasts
        
    except ImportError as e:
        logger.error(f"Import error in ML forecast: {e}")
        return None
    except Exception as e:
        logger.error(f"ML forecast failed: {e}")
        return None

def _rule_based_forecast(
    sector: str,
    region: str,
    horizon: int
) -> List[float]:
    """
    Generate forecast using rule-based approach.
    
    Args:
        sector: Sector name
        region: Region name
        horizon: Number of weeks
    
    Returns:
        List[float]: Forecast values
    """
    # Get base demand
    base = _SECTOR_BASE.get(sector, 200)
    
    # Get regional multiplier
    region_mult = _REGION_MULTIPLIERS.get(region, 1.0)
    
    # Generate forecast with seasonal patterns
    now = datetime.datetime.now()
    woy_0 = now.isocalendar()[1]
    forecasts = []
    
    # Use a fixed seed for reproducibility
    rng = np.random.RandomState(42)
    
    for i in range(horizon):
        woy = (woy_0 + i) % 52 or 52
        
        # Seasonal factor (sinusoidal)
        season = 1 + 0.25 * np.sin(2 * np.pi * woy / 52)
        
        # Holiday factor
        holiday = _HOLIDAY_WEEKS.get(woy, 1.0)
        
        # Harvest factor (lower demand during harvest)
        harvest = 0.85 if woy in _HARVEST_WEEKS else 1.0
        
        # Random variation (±5%)
        noise = 1.0 + rng.normal(0, 0.05)
        
        # Calculate demand
        demand = base * season * holiday * harvest * noise * region_mult
        demand = max(0, demand)
        
        forecasts.append(round(demand, 1))
    
    return forecasts

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def _get_commodity(product: Optional[str], sector: str) -> str:
    """
    Get standardized commodity name from product or sector.
    
    Args:
        product: Product name (optional)
        sector: Sector name
    
    Returns:
        str: Standardized commodity name
    """
    if product:
        product_lower = product.lower().strip()
        # Check for exact match
        if product_lower in _COMMODITY_MAP:
            return _COMMODITY_MAP[product_lower]
        
        # Check for partial match
        for key, value in _COMMODITY_MAP.items():
            if key in product_lower:
                return value
    
    # Fallback to sector mapping
    sector_lower = sector.lower().strip()
    for key, value in _COMMODITY_MAP.items():
        if key in sector_lower:
            return value
    
    return "Teff"  # Default commodity

def _get_base_demand(
    historical_data: Optional[List[float]],
    sector: str
) -> float:
    """
    Get base demand from historical data or sector default.
    
    Args:
        historical_data: List of historical demand values
        sector: Sector name
    
    Returns:
        float: Base demand value
    """
    if historical_data and len(historical_data) > 0:
        # Use the most recent value if available
        return float(historical_data[-1])
    else:
        # Use sector default
        return float(_SECTOR_BASE.get(sector, 200))

# ─────────────────────────────────────────────────────────────
# ENHANCED FORECASTING FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_demand_trend(
    sector: str = "Agriculture",
    product: Optional[str] = None,
    region: str = "Oromia",
    weeks: int = 12
) -> Dict[str, Any]:
    """
    Get demand trend with additional statistics.
    
    Args:
        sector: Sector name
        product: Product name (optional)
        region: Region name
        weeks: Number of weeks to forecast
    
    Returns:
        Dict: Forecast with statistics
    """
    forecasts = forecast_demand(
        sector=sector,
        product=product,
        region=region,
        horizon=weeks
    )
    
    if not forecasts:
        return {
            "forecast": [],
            "average": 0,
            "peak": 0,
            "trough": 0,
            "trend": "stable",
            "confidence": "low"
        }
    
    avg_demand = np.mean(forecasts)
    peak_demand = max(forecasts)
    trough_demand = min(forecasts)
    
    # Determine trend
    if len(forecasts) >= 2:
        first_half = np.mean(forecasts[:len(forecasts)//2])
        second_half = np.mean(forecasts[len(forecasts)//2:])
        if second_half > first_half * 1.05:
            trend = "increasing"
        elif second_half < first_half * 0.95:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return {
        "forecast": forecasts,
        "average": round(avg_demand, 1),
        "peak": round(peak_demand, 1),
        "trough": round(trough_demand, 1),
        "trend": trend,
        "confidence": "medium" if len(forecasts) > 4 else "low"
    }

def get_demand_summary(
    sector: str = "Agriculture",
    product: Optional[str] = None,
    region: str = "Oromia"
) -> Dict[str, Any]:
    """
    Get a summary of demand forecast.
    
    Args:
        sector: Sector name
        product: Product name (optional)
        region: Region name
    
    Returns:
        Dict: Summary of demand forecast
    """
    # Get 12-week forecast
    result = get_demand_trend(sector, product, region, weeks=12)
    
    # Get 4-week short-term forecast
    short_term = forecast_demand(sector, product, region, horizon=4)
    
    # Get long-term forecast (26 weeks)
    long_term = forecast_demand(sector, product, region, horizon=26)
    
    return {
        "short_term": short_term[:4] if short_term else [],
        "medium_term": result["forecast"],
        "long_term_trend": result["trend"],
        "average_demand": result["average"],
        "peak_demand": result["peak"],
        "trough_demand": result["trough"],
        "confidence": result["confidence"],
        "sector": sector,
        "region": region,
        "commodity": _get_commodity(product, sector) if product else sector
    }

def get_seasonal_pattern(sector: str = "Agriculture") -> Dict[str, Any]:
    """
    Get seasonal demand pattern for a sector.
    
    Args:
        sector: Sector name
    
    Returns:
        Dict: Seasonal pattern information
    """
    # Generate a full year of demand
    forecasts = forecast_demand(sector, horizon=52)
    
    if not forecasts:
        return {"pattern": [], "peak_weeks": [], "trough_weeks": []}
    
    # Find peaks and troughs
    peak_threshold = np.percentile(forecasts, 80)
    trough_threshold = np.percentile(forecasts, 20)
    
    peak_weeks = [i for i, v in enumerate(forecasts) if v > peak_threshold]
    trough_weeks = [i for i, v in enumerate(forecasts) if v < trough_threshold]
    
    return {
        "pattern": forecasts,
        "peak_weeks": peak_weeks,
        "trough_weeks": trough_weeks,
        "max_demand": max(forecasts),
        "min_demand": min(forecasts),
        "avg_demand": np.mean(forecasts)
    }

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Demand Forecasting Engine")
    print("=" * 50)
    
    # Test with different sectors
    sectors = ["Agriculture", "Livestock", "Food Processing"]
    for sector in sectors:
        forecast = forecast_demand(sector=sector, horizon=12)
        print(f"\n📊 {sector} 12-week forecast:")
        print(f"  {forecast}")
        print(f"  Average: {np.mean(forecast):.1f}")
        print(f"  Peak: {max(forecast):.1f}")
        print(f"  Trend: {get_demand_trend(sector=sector)['trend']}")
    
    # Test with product
    print(f"\n📦 Coffee forecast:")
    coffee_forecast = forecast_demand(sector="Agriculture", product="Coffee", horizon=12)
    print(f"  {coffee_forecast}")
    
    # Test with regional variation
    print(f"\n📍 Regional variation:")
    for region in ["Addis Ababa", "Oromia", "Afar"]:
        forecast = forecast_demand(sector="Agriculture", region=region, horizon=4)
        print(f"  {region}: {forecast}")
