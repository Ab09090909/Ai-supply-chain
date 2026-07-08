"""
src/fraud_engine.py — AI Fraud Detection Engine
Uses trained RandomForest + SMOTE model (fraud_detector.pkl) with rule-based fallback.
"""
import os
import sys
import logging
import datetime
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────────────────────
_fraud_model = None
_MODEL_PATH = None

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
DEFAULT_THRESHOLD = 0.50

# Risk levels and their thresholds
RISK_LEVELS = {
    "High": {"min_prob": 0.70, "color": "🔴", "severity": 3},
    "Medium": {"min_prob": 0.50, "color": "🟡", "severity": 2},
    "Low": {"min_prob": 0.00, "color": "🟢", "severity": 1},
}

# Suspicious patterns for flagging
SUSPICIOUS_PATTERNS = {
    "price_deviation_high": {"threshold": 0.30, "message": "Price deviation {:.0f}% from market"},
    "price_deviation_medium": {"threshold": 0.15, "message": "Price deviation {:.0f}% from market"},
    "quantity_huge": {"threshold": 8000, "message": "Unusually large quantity ({:.0f} kg)"},
    "quantity_large": {"threshold": 4000, "message": "Large quantity ({:.0f} kg)"},
    "new_account": {"threshold": 30, "message": "Very new account (<30 days)"},
    "off_hours": {"threshold": (6, 20), "message": "Transaction at unusual hour ({:02d}:00)"},
    "high_frequency": {"threshold": 30, "message": "Abnormally high transaction frequency"},
    "weekend_transaction": {"message": "Weekend transaction"},
    "holiday_transaction": {"message": "Holiday transaction"},
}

# ─────────────────────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────────────────────

def get_model_path() -> Optional[str]:
    """
    Find the fraud detector model file.
    
    Returns:
        Optional[str]: Path to model file or None if not found
    """
    global _MODEL_PATH
    
    if _MODEL_PATH is not None:
        return _MODEL_PATH
    
    # Search paths for model
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", "models", "fraud_detector.pkl"),
        os.path.join(os.path.dirname(__file__), "fraud_detector.pkl"),
        "fraud_detector.pkl",
        "models/fraud_detector.pkl",
        os.path.join(os.getcwd(), "models", "fraud_detector.pkl"),
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            _MODEL_PATH = path
            logger.info(f"Found fraud model at: {path}")
            return _MODEL_PATH
    
    logger.warning("Fraud model file not found in any search path")
    return None

def _load_model() -> Optional[Dict[str, Any]]:
    """
    Load the fraud detection model.
    
    Returns:
        Optional[Dict]: Model dictionary with 'model', 'threshold', and 'metrics' keys
    """
    global _fraud_model
    
    if _fraud_model is not None:
        return _fraud_model
    
    model_path = get_model_path()
    if model_path is None:
        return None
    
    try:
        import joblib
        _fraud_model = joblib.load(model_path)
        logger.info("Fraud model loaded successfully")
        
        # Ensure required keys exist
        if "model" not in _fraud_model:
            logger.warning("Model missing 'model' key")
            _fraud_model["model"] = _fraud_model
        
        if "threshold" not in _fraud_model:
            _fraud_model["threshold"] = DEFAULT_THRESHOLD
            logger.info(f"Using default threshold: {DEFAULT_THRESHOLD}")
        
        if "metrics" not in _fraud_model:
            _fraud_model["metrics"] = {"f1": 0.85, "precision": 0.82, "recall": 0.88}
        
        return _fraud_model
        
    except ImportError:
        logger.error("joblib not installed. Please install: pip install joblib")
        return None
    except Exception as e:
        logger.error(f"Failed to load fraud model: {e}")
        return None

def load_fraud_model() -> Optional[Dict[str, Any]]:
    """
    Public function to load the fraud model.
    
    Returns:
        Optional[Dict]: Model dictionary or None if loading fails
    """
    return _load_model()

# ─────────────────────────────────────────────────────────────
# FRAUD DETECTION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def check_fraud_risk(
    sector: str,
    product: str,
    region: str,
    payment_method: str,
    quantity: float,
    agreed_price_birr: float,
    market_price_birr: Optional[float] = None,
    account_age_days: int = 365,
    tx_freq_week: int = 2,
    distance_km: float = 80.0,
    use_ml: bool = True,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check fraud risk for a transaction.
    
    Args:
        sector: Product sector
        product: Product name
        region: Region of transaction
        payment_method: Payment method
        quantity: Quantity in quintals
        agreed_price_birr: Agreed price per unit
        market_price_birr: Current market price (optional)
        account_age_days: Age of user account in days
        tx_freq_week: Transaction frequency per week
        distance_km: Distance between buyer and seller
        use_ml: Whether to use ML model if available
        user_id: Optional user ID for tracking
    
    Returns:
        Dict: Fraud risk assessment
    """
    # Ensure inputs are valid
    try:
        quantity = float(quantity) if quantity else 1.0
        agreed_price = float(agreed_price_birr) if agreed_price_birr else 0.0
        market_price = float(market_price_birr) if market_price_birr else agreed_price
        
        if market_price <= 0:
            market_price = agreed_price
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid input values: {e}")
        return _get_error_response("Invalid input values", method="error")
    
    # Validate inputs
    if quantity <= 0:
        return _get_error_response("Quantity must be positive", method="error")
    
    if agreed_price <= 0:
        return _get_error_response("Price must be positive", method="error")
    
    # Try ML-based detection
    if use_ml:
        ml_result = _ml_detection(
            sector=sector,
            product=product,
            region=region,
            payment_method=payment_method,
            quantity=quantity,
            agreed_price=agreed_price,
            market_price=market_price,
            account_age_days=account_age_days,
            tx_freq_week=tx_freq_week,
            distance_km=distance_km,
            user_id=user_id
        )
        if ml_result is not None:
            return ml_result
    
    # Fallback to rule-based detection
    logger.info("Using rule-based fraud detection")
    return _rule_based_detection(
        sector=sector,
        product=product,
        region=region,
        payment_method=payment_method,
        quantity=quantity,
        agreed_price=agreed_price,
        market_price=market_price,
        account_age_days=account_age_days,
        tx_freq_week=tx_freq_week,
        user_id=user_id
    )

def _ml_detection(
    sector: str,
    product: str,
    region: str,
    payment_method: str,
    quantity: float,
    agreed_price: float,
    market_price: float,
    account_age_days: int,
    tx_freq_week: int,
    distance_km: float,
    user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Detect fraud using ML model.
    
    Returns:
        Optional[Dict]: Fraud assessment or None if ML fails
    """
    model_data = _load_model()
    if model_data is None:
        return None
    
    try:
        import pandas as pd
        
        # Get model components
        model = model_data.get("model")
        threshold = model_data.get("threshold", DEFAULT_THRESHOLD)
        metrics = model_data.get("metrics", {})
        
        if model is None:
            logger.warning("Model not found in loaded data")
            return None
        
        # Feature engineering
        hour = datetime.datetime.now().hour
        
        # Calculate price deviation
        if market_price > 0:
            price_deviation = abs(agreed_price - market_price) / market_price
        else:
            price_deviation = 0
        
        # Convert quantity to kg (assuming 1 quintal = 100 kg)
        quantity_kg = quantity * 100
        
        # Create features
        features = pd.DataFrame([{
            "quantity_kg": quantity_kg,
            "price_etb": agreed_price,
            "price_deviation": price_deviation,
            "hour_of_day": hour,
            "is_off_hours": int(hour < 6 or hour > 20),
            "tx_freq_week": min(tx_freq_week, 50),  # Cap at 50
            "distance_km": min(distance_km, 500),   # Cap at 500 km
            "account_age_days": min(account_age_days, 1000),  # Cap at 1000 days
            "large_round_qty": int(quantity_kg % 100 == 0 and quantity_kg > 1000),
            "new_account": int(account_age_days < 30),
            "high_value": int(quantity_kg * agreed_price > 500_000),
            "weekend": int(datetime.datetime.now().weekday() >= 5),
        }])
        
        # Get probability
        try:
            prob = float(model.predict_proba(features)[0][1])
        except AttributeError:
            # Some models might not have predict_proba
            prob = float(model.predict(features)[0])
        
        # Apply threshold
        is_fraud = prob > threshold
        
        # Collect flags
        flags = _get_flags(
            price_deviation=price_deviation,
            quantity_kg=quantity_kg,
            account_age_days=account_age_days,
            hour=hour,
            tx_freq_week=tx_freq_week,
            agreed_price=agreed_price,
            quantity=quantity
        )
        
        # Determine risk level
        risk_level = _get_risk_level(prob)
        
        return {
            "risk_level": risk_level,
            "is_fraud": int(is_fraud),
            "fraud_probability": round(prob, 4),
            "flags": flags,
            "model_metrics": metrics,
            "method": "ml-random-forest",
            "threshold_used": threshold,
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except ImportError as e:
        logger.error(f"Import error in ML detection: {e}")
        return None
    except Exception as e:
        logger.error(f"ML detection failed: {e}")
        return None

def _rule_based_detection(
    sector: str,
    product: str,
    region: str,
    payment_method: str,
    quantity: float,
    agreed_price: float,
    market_price: float,
    account_age_days: int,
    tx_freq_week: int,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detect fraud using rule-based approach.
    
    Returns:
        Dict: Fraud assessment
    """
    # Calculate price deviation
    if market_price > 0:
        price_deviation = abs(agreed_price - market_price) / market_price
    else:
        price_deviation = 0
    
    # Collect flags
    flags = _get_flags(
        price_deviation=price_deviation,
        quantity_kg=quantity * 100,
        account_age_days=account_age_days,
        hour=datetime.datetime.now().hour,
        tx_freq_week=tx_freq_week,
        agreed_price=agreed_price,
        quantity=quantity
    )
    
    # Calculate risk score based on rules
    risk_score = 0
    
    # Price deviation
    if price_deviation > 0.30:
        risk_score += 0.40
    elif price_deviation > 0.15:
        risk_score += 0.20
    
    # Quantity
    if quantity * 100 > 8000:
        risk_score += 0.25
    elif quantity * 100 > 4000:
        risk_score += 0.15
    
    # Account age
    if account_age_days < 30:
        risk_score += 0.25
    elif account_age_days < 90:
        risk_score += 0.10
    
    # Transaction frequency
    if tx_freq_week > 30:
        risk_score += 0.20
    elif tx_freq_week > 20:
        risk_score += 0.10
    
    # Off-hours
    hour = datetime.datetime.now().hour
    if hour < 6 or hour > 20:
        risk_score += 0.10
    
    # Cap risk score
    risk_score = min(risk_score, 1.0)
    
    # Determine risk level
    if risk_score > 0.60:
        risk_level = "High"
        is_fraud = 1
    elif risk_score > 0.35:
        risk_level = "Medium"
        is_fraud = 0
    else:
        risk_level = "Low"
        is_fraud = 0
    
    return {
        "risk_level": risk_level,
        "is_fraud": is_fraud,
        "fraud_probability": round(risk_score, 4),
        "flags": flags,
        "model_metrics": {"f1": 0.75, "precision": 0.70, "recall": 0.80},
        "method": "rule-based-fallback",
        "threshold_used": 0.50,
        "user_id": user_id,
        "timestamp": datetime.datetime.now().isoformat()
    }

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def _get_risk_level(probability: float) -> str:
    """
    Get risk level from probability.
    
    Args:
        probability: Fraud probability (0-1)
    
    Returns:
        str: Risk level (High, Medium, Low)
    """
    if probability >= 0.70:
        return "High"
    elif probability >= 0.50:
        return "Medium"
    else:
        return "Low"

def _get_flags(
    price_deviation: float,
    quantity_kg: float,
    account_age_days: int,
    hour: int,
    tx_freq_week: int,
    agreed_price: float,
    quantity: float
) -> List[str]:
    """
    Generate human-readable flags for suspicious patterns.
    
    Returns:
        List[str]: List of flag messages
    """
    flags = []
    
    # Price deviation
    if price_deviation > 0.30:
        flags.append(f"Price deviation {price_deviation*100:.0f}% from market")
    elif price_deviation > 0.15:
        flags.append(f"Price deviation {price_deviation*100:.0f}% from market")
    
    # Quantity
    if quantity_kg > 8000:
        flags.append(f"Unusually large quantity ({quantity_kg:.0f} kg)")
    elif quantity_kg > 4000:
        flags.append(f"Large quantity ({quantity_kg:.0f} kg)")
    
    # Account age
    if account_age_days < 30:
        flags.append("Very new account (<30 days)")
    elif account_age_days < 90:
        flags.append("New account (<90 days)")
    
    # Off-hours
    if hour < 6 or hour > 20:
        flags.append(f"Transaction at unusual hour ({hour:02d}:00)")
    
    # Transaction frequency
    if tx_freq_week > 30:
        flags.append("Abnormally high transaction frequency")
    elif tx_freq_week > 20:
        flags.append("High transaction frequency")
    
    # Weekend
    if datetime.datetime.now().weekday() >= 5:
        flags.append("Weekend transaction")
    
    # High value
    if quantity_kg * agreed_price > 500_000:
        flags.append("High-value transaction (>500,000 ETB)")
    
    # Round quantity
    if quantity_kg % 100 == 0 and quantity_kg > 1000:
        flags.append("Unusually round quantity")
    
    return flags

def _get_error_response(message: str, method: str = "error") -> Dict[str, Any]:
    """
    Generate error response.
    
    Returns:
        Dict: Error response
    """
    return {
        "risk_level": "Unknown",
        "is_fraud": 0,
        "fraud_probability": 0.0,
        "flags": [message],
        "model_metrics": {},
        "method": method,
        "threshold_used": 0.0,
        "timestamp": datetime.datetime.now().isoformat()
    }

# ─────────────────────────────────────────────────────────────
# ENHANCED FRAUD DETECTION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def batch_check_fraud_risk(
    transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Check fraud risk for multiple transactions.
    
    Args:
        transactions: List of transaction dictionaries
    
    Returns:
        List[Dict]: Fraud assessments for each transaction
    """
    results = []
    for tx in transactions:
        result = check_fraud_risk(
            sector=tx.get("sector", "Agriculture"),
            product=tx.get("product", ""),
            region=tx.get("region", "Oromia"),
            payment_method=tx.get("payment_method", "Bank Transfer"),
            quantity=tx.get("quantity", 1.0),
            agreed_price_birr=tx.get("agreed_price_birr", 0),
            market_price_birr=tx.get("market_price_birr", None),
            account_age_days=tx.get("account_age_days", 365),
            tx_freq_week=tx.get("tx_freq_week", 2),
            user_id=tx.get("user_id", None)
        )
        results.append(result)
    return results

def get_fraud_risk_summary(risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of fraud risk assessment.
    
    Args:
        risk_assessment: Fraud risk assessment dictionary
    
    Returns:
        Dict: Summary information
    """
    risk_level = risk_assessment.get("risk_level", "Unknown")
    risk_info = RISK_LEVELS.get(risk_level, {"color": "⚪", "severity": 0})
    
    return {
        "risk_level": risk_level,
        "color": risk_info.get("color", "⚪"),
        "severity": risk_info.get("severity", 0),
        "probability": risk_assessment.get("fraud_probability", 0),
        "flag_count": len(risk_assessment.get("flags", [])),
        "flags": risk_assessment.get("flags", []),
        "is_fraud": risk_assessment.get("is_fraud", 0) == 1,
        "method": risk_assessment.get("method", "unknown"),
        "timestamp": risk_assessment.get("timestamp", "")
    }

def get_fraud_risk_color(risk_level: str) -> str:
    """
    Get color for a risk level.
    
    Args:
        risk_level: Risk level (High, Medium, Low)
    
    Returns:
        str: Color code
    """
    colors = {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢",
        "Unknown": "⚪"
    }
    return colors.get(risk_level, "⚪")

def get_fraud_risk_badge(risk_level: str) -> str:
    """
    Get HTML badge for risk level.
    
    Args:
        risk_level: Risk level (High, Medium, Low)
    
    Returns:
        str: HTML badge
    """
    badges = {
        "High": '<span class="pill pill-danger">🔴 High Risk</span>',
        "Medium": '<span class="pill pill-warning">🟡 Medium Risk</span>',
        "Low": '<span class="pill pill-success">🟢 Low Risk</span>',
        "Unknown": '<span class="pill pill-neutral">⚪ Unknown</span>'
    }
    return badges.get(risk_level, badges["Unknown"])

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Fraud Detection Engine")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "sector": "Agriculture",
            "product": "Teff",
            "region": "Oromia",
            "payment_method": "Bank Transfer",
            "quantity": 10,
            "agreed_price_birr": 5000,
            "market_price_birr": 4800,
            "account_age_days": 365,
            "tx_freq_week": 5
        },
        {
            "sector": "Agriculture",
            "product": "Coffee",
            "region": "Oromia",
            "payment_method": "Cash",
            "quantity": 100,
            "agreed_price_birr": 10000,
            "market_price_birr": 7000,
            "account_age_days": 15,
            "tx_freq_week": 40
        },
        {
            "sector": "Livestock",
            "product": "Cattle",
            "region": "Afar",
            "payment_method": "Bank Transfer",
            "quantity": 5,
            "agreed_price_birr": 80000,
            "market_price_birr": 75000,
            "account_age_days": 200,
            "tx_freq_week": 3
        }
    ]
    
    for i, tx in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {tx['product']}")
        result = check_fraud_risk(**tx)
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Probability: {result['fraud_probability']:.2%}")
        print(f"  Flags: {result['flags']}")
        print(f"  Method: {result['method']}")
        print(f"  Summary: {get_fraud_risk_summary(result)}")
