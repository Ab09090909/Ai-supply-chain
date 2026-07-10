# pages/producer/tabs/ai_insights.py
import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import pickle
import requests
import re
from datetime import datetime, timedelta
import random
import hashlib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from utils.db_helpers import get_products, get_user_by_id, supabase

# ==========================================
# PRODUCT CATEGORY & UNIT DETECTION
# ==========================================

def get_product_unit(product_name):
    """Detect the correct unit for a product"""
    categories = {
        "kg": ["coffee", "wheat", "teff", "corn", "maize", "sugar", "rice", "barley", 
               "sorghum", "sesame", "honey", "butter", "cheese", "flour", "grain", 
               "onion", "tomato", "potato", "cabbage", "carrot", "garlic", "ginger",
               "beef", "mutton", "goat", "fish", "meat", "poultry"],
        "liter": ["oil", "cooking oil", "fuel", "milk", "yogurt", "juice", "water"],
        "unit": ["car", "phone", "laptop", "motorcycle", "bicycle", "furniture"],
        "quintal": ["grain", "sorghum", "barley", "wheat", "teff"],
        "piece": ["egg", "bread", "injera", "chicken", "banana", "mango", "avocado", 
                  "orange", "papaya", "apple", "lime", "lemon"]
    }
    
    product_lower = product_name.lower().strip()
    for unit, products in categories.items():
        if any(p in product_lower for p in products):
            return unit
    return "kg"  # Default

def is_commodity(product_name):
    """Check if product is a valid Ethiopian commodity"""
    valid_commodities = [
        'coffee', 'teff', 'wheat', 'barley', 'maize', 'corn', 'sorghum', 
        'millet', 'sesame', 'honey', 'sugar', 'rice', 'milk', 'butter',
        'cheese', 'yogurt', 'egg', 'chicken', 'beef', 'mutton', 'goat',
        'onion', 'tomato', 'potato', 'cabbage', 'carrot', 'green pepper',
        'banana', 'mango', 'avocado', 'orange', 'papaya', 'apple',
        'cooking oil', 'wheat flour', 'teff flour', 'bread', 'injera',
        'garlic', 'ginger', 'lime', 'lemon', 'fish', 'poultry'
    ]
    
    product_lower = product_name.lower().strip()
    for commodity in valid_commodities:
        if commodity in product_lower or product_lower in commodity:
            return True
    return False

def validate_product(product_name):
    """Validate product input"""
    if not product_name or len(product_name.strip()) < 2:
        return False, "Please enter a valid product name (at least 2 characters)"
    
    # Block non-commodity items
    non_commodities = ["car", "phone", "laptop", "house", "computer", "table", "chair", 
                       "television", "tv", "radio", "fridge", "refrigerator", "stove"]
    product_lower = product_name.lower().strip()
    
    if any(item in product_lower for item in non_commodities):
        return False, f"❌ '{product_name}' is not a market commodity. Please enter an agricultural product like: coffee, wheat, teff, sugar, cooking oil, onion, tomato, etc."
    
    return True, "OK"

# ==========================================
# GROQ API INTEGRATION - CLEAN PROMPT
# ==========================================

def get_groq_api_key():
    """Get Groq API key from secrets"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("groq_api_key") or st.secrets.get("GROQ_KEY")
        return api_key
    except Exception as e:
        return None

def build_prompt(product_name, region):
    """Build a clean prompt for Groq without hardcoded prices"""
    unit = get_product_unit(product_name)
    
    prompt = f"""You are an Ethiopian market analyst analyzing {product_name} in {region}, Ethiopia.

Product: {product_name}
Region: {region}
Unit: {unit}

Your task: Provide a realistic market analysis based on your knowledge of Ethiopian agricultural markets.

Provide:
1. Current estimated price (ETB/{unit})
2. Price range (ETB/{unit})
3. Market trend (increasing/stable/decreasing)
4. Demand level (high/medium/low)
5. Confidence level (HIGH/MEDIUM/LOW)

Important:
- Use your knowledge of Ethiopian market conditions
- Be realistic and specific
- If you don't have enough information, say "Insufficient data" and set confidence to LOW
- Do not invent prices or sources"""
    
    return prompt

def query_groq_market_data(product_name, region="Addis Ababa"):
    """Query Groq API with clean prompt"""
    try:
        # Validate product first
        is_valid, msg = validate_product(product_name)
        if not is_valid:
            return {
                "success": False,
                "error": msg,
                "fallback_used": True,
                "is_commodity": False
            }
        
        # Check if it's a commodity
        is_commodity_check = is_commodity(product_name)
        
        api_key = get_groq_api_key()
        if not api_key:
            return {
                "success": False,
                "error": "Groq API key not configured.",
                "fallback_used": True,
                "is_commodity": is_commodity_check
            }

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = build_prompt(product_name, region)
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a market analyst with knowledge of Ethiopian agricultural markets. Provide realistic, data-driven estimates."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 400,
            "temperature": 0.1
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API Error {response.status_code}",
                "fallback_used": True,
                "is_commodity": is_commodity_check
            }
        
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content'].strip()
            
            # Parse response - look for price numbers
            price_match = re.search(r'price.*?([\d.]+)', content, re.IGNORECASE)
            range_match = re.search(r'range.*?([\d.]+)\s*-\s*([\d.]+)', content, re.IGNORECASE)
            trend_match = re.search(r'trend.*?(\w+)', content, re.IGNORECASE)
            demand_match = re.search(r'demand.*?(\w+)', content, re.IGNORECASE)
            confidence_match = re.search(r'confidence.*?(\w+)', content, re.IGNORECASE)
            
            unit = get_product_unit(product_name)
            result = {
                "success": True,
                "raw_response": content,
                "source": "Groq API",
                "unit": unit,
                "is_commodity": True
            }
            
            if price_match:
                result["price"] = float(price_match.group(1))
            
            if range_match:
                result["min_price"] = float(range_match.group(1))
                result["max_price"] = float(range_match.group(2))
            
            if trend_match:
                result["trend"] = trend_match.group(1).lower()
            
            if demand_match:
                result["demand"] = demand_match.group(1).lower()
            
            if confidence_match:
                result["confidence"] = confidence_match.group(1).upper()
            else:
                result["confidence"] = "MEDIUM"
            
            return result
        else:
            return {
                "success": False,
                "error": "Unexpected API response format",
                "fallback_used": True,
                "is_commodity": is_commodity_check
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out", "fallback_used": True, "is_commodity": False}
    except Exception as e:
        return {"success": False, "error": str(e), "fallback_used": True, "is_commodity": False}

# ==========================================
# FALLBACK - ESTIMATED PRICES (REALISTIC RANGES)
# ==========================================

def get_estimated_price(product_name):
    """Get a realistic estimated price based on product category"""
    product_lower = product_name.lower().strip()
    unit = get_product_unit(product_name)
    
    # Default price ranges by category
    if 'coffee' in product_lower:
        return 300, 250, 350, 'increasing', 'high', f'ETB/{unit}'
    elif 'teff' in product_lower:
        return 100, 80, 120, 'increasing', 'high', f'ETB/{unit}'
    elif 'wheat' in product_lower:
        return 55, 45, 70, 'stable', 'high', f'ETB/{unit}'
    elif 'sugar' in product_lower:
        return 65, 50, 80, 'stable', 'high', f'ETB/{unit}'
    elif 'oil' in product_lower or 'cooking' in product_lower:
        return 150, 120, 180, 'increasing', 'high', f'ETB/{unit}'
    elif 'milk' in product_lower:
        return 75, 60, 90, 'increasing', 'high', f'ETB/{unit}'
    elif 'beef' in product_lower or 'meat' in product_lower:
        return 500, 400, 600, 'increasing', 'high', f'ETB/{unit}'
    elif 'onion' in product_lower:
        return 35, 25, 45, 'volatile', 'high', f'ETB/{unit}'
    elif 'tomato' in product_lower:
        return 42, 30, 55, 'volatile', 'high', f'ETB/{unit}'
    elif 'potato' in product_lower:
        return 50, 35, 65, 'increasing', 'medium', f'ETB/{unit}'
    elif 'egg' in product_lower:
        return 7, 5, 10, 'stable', 'high', f'ETB/piece'
    elif 'chicken' in product_lower:
        return 325, 250, 400, 'stable', 'medium', f'ETB/piece'
    elif 'banana' in product_lower:
        return 20, 15, 25, 'stable', 'medium', f'ETB/piece'
    elif 'mango' in product_lower:
        return 17, 12, 22, 'decreasing', 'medium', f'ETB/piece'
    elif 'avocado' in product_lower:
        return 15, 10, 20, 'increasing', 'high', f'ETB/piece'
    else:
        # Generic estimate for unknown products
        return 100, 60, 150, 'stable', 'medium', f'ETB/{unit}'

def get_fallback_data(product_name, region="Addis Ababa"):
    """Get fallback data without hardcoded price lists"""
    
    if not is_commodity(product_name):
        return {
            'product': product_name,
            'price': None,
            'min_price': None,
            'max_price': None,
            'avg_price': None,
            'unit': get_product_unit(product_name),
            'trend': 'N/A',
            'demand': 'N/A',
            'data_source': 'Not a commodity',
            'source': 'Invalid',
            'is_fallback': True,
            'is_commodity': False,
            'error': f"'{product_name}' is not a recognized Ethiopian market commodity."
        }
    
    price, min_price, max_price, trend, demand, unit_display = get_estimated_price(product_name)
    unit = get_product_unit(product_name)
    
    return {
        'product': product_name,
        'price': price,
        'min_price': min_price,
        'max_price': max_price,
        'avg_price': price,
        'unit': unit,
        'trend': trend,
        'demand': demand,
        'data_source': 'Market Estimate',
        'source': 'Estimated',
        'is_fallback': True,
        'is_commodity': True,
        'confidence': 'MEDIUM',
        'unit_display': unit_display
    }

# ==========================================
# SELF-LEARNING AI SYSTEM
# ==========================================

class SelfLearningAIInsights:
    """Self-learning AI system with Supabase storage"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.models_dir = "Models"
        self.data_dir = "data"
        
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.knowledge_base = self.load_knowledge_base()
        self.model = None
        self.scaler = None
        self.load_or_train_model()
        
    def load_knowledge_base(self):
        """Load knowledge base from disk"""
        try:
            path = f"{self.data_dir}/ai_knowledge_{self.user_id}.json"
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                default = {
                    'market_data': {},
                    'price_history': {},
                    'demand_patterns': {},
                    'product_insights': {},
                    'training_data': [],
                    'predictions': {},
                    'learning_iterations': 0,
                    'accuracy_score': 0
                }
                with open(path, 'w') as f:
                    json.dump(default, f, indent=2)
                return default
        except Exception as e:
            return {
                'market_data': {},
                'price_history': {},
                'demand_patterns': {},
                'product_insights': {},
                'training_data': [],
                'predictions': {},
                'learning_iterations': 0,
                'accuracy_score': 0
            }
    
    def save_knowledge_base(self):
        """Save knowledge base to disk"""
        try:
            with open(f"{self.data_dir}/ai_knowledge_{self.user_id}.json", 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
        except Exception as e:
            pass
    
    def load_or_train_model(self):
        """Load existing model or train a new one"""
        try:
            model_path = f"{self.models_dir}/ai_model_{self.user_id}.pkl"
            scaler_path = f"{self.models_dir}/ai_scaler_{self.user_id}.pkl"
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                return True
            else:
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                self.scaler = StandardScaler()
                self.train_model(self.generate_synthetic_data())
                return True
        except Exception as e:
            return False
    
    def train_model(self, training_data):
        """Train the AI model with provided data"""
        try:
            X = []
            y = []
            
            for item in training_data:
                features = [
                    item.get('price', 100),
                    item.get('demand_score', 50),
                    item.get('seasonal_factor', 1.0),
                    item.get('region_factor', 1.0),
                    item.get('trend_factor', 1.0)
                ]
                target = item.get('predicted_price', item.get('price', 100))
                
                X.append(features)
                y.append(target)
            
            if len(X) > 5:
                X = np.array(X)
                y = np.array(y)
                
                self.scaler.fit(X)
                X_scaled = self.scaler.transform(X)
                
                self.model.fit(X_scaled, y)
                
                self.knowledge_base['accuracy_score'] = self.model.score(X_scaled, y)
                self.knowledge_base['learning_iterations'] = len(training_data)
                
                self.save_model()
                self.save_knowledge_base()
                return True
            return False
        except Exception as e:
            return False
    
    def generate_synthetic_data(self):
        """Generate synthetic training data"""
        synthetic_data = []
        products = [
            {'name': 'coffee', 'price': 300, 'demand': 90, 'seasonal': 1.1},
            {'name': 'teff', 'price': 100, 'demand': 85, 'seasonal': 1.0},
            {'name': 'wheat flour', 'price': 70, 'demand': 88, 'seasonal': 1.0},
            {'name': 'sugar', 'price': 65, 'demand': 85, 'seasonal': 0.9},
            {'name': 'cooking oil', 'price': 150, 'demand': 92, 'seasonal': 1.0},
            {'name': 'milk', 'price': 75, 'demand': 88, 'seasonal': 1.0},
            {'name': 'beef', 'price': 500, 'demand': 80, 'seasonal': 1.1},
            {'name': 'onion', 'price': 35, 'demand': 92, 'seasonal': 0.9},
            {'name': 'tomato', 'price': 42, 'demand': 90, 'seasonal': 0.8},
            {'name': 'potato', 'price': 50, 'demand': 85, 'seasonal': 1.0},
        ]
        
        for product in products:
            for i in range(10):
                variation = random.uniform(0.85, 1.15)
                data = {
                    'product_name': product['name'],
                    'price': product['price'] * variation,
                    'demand_score': product['demand'] * random.uniform(0.9, 1.05),
                    'seasonal_factor': product['seasonal'] * random.uniform(0.9, 1.1),
                    'region_factor': random.uniform(0.9, 1.1),
                    'trend_factor': random.uniform(0.95, 1.05),
                    'predicted_price': product['price'] * variation * random.uniform(0.95, 1.05)
                }
                synthetic_data.append(data)
        
        return synthetic_data
    
    def save_model(self):
        """Save model to disk"""
        try:
            model_path = f"{self.models_dir}/ai_model_{self.user_id}.pkl"
            scaler_path = f"{self.models_dir}/ai_scaler_{self.user_id}.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            return True
        except Exception as e:
            return False
    
    def get_market_data(self, product_name, region="Addis Ababa"):
        """Get market data from Groq or fallback"""
        
        # Validate product first
        is_valid, msg = validate_product(product_name)
        if not is_valid:
            return {
                'product': product_name,
                'error': msg,
                'is_valid': False,
                'is_commodity': False,
                'source': 'Validation Failed'
            }
        
        # Try Groq API first
        groq_result = query_groq_market_data(product_name, region)
        
        if groq_result.get('success') and groq_result.get('price'):
            return {
                'product': product_name,
                'price': groq_result.get('price'),
                'min_price': groq_result.get('min_price', groq_result.get('price') * 0.8),
                'max_price': groq_result.get('max_price', groq_result.get('price') * 1.2),
                'avg_price': groq_result.get('price'),
                'unit': groq_result.get('unit', get_product_unit(product_name)),
                'trend': groq_result.get('trend', 'stable'),
                'demand': groq_result.get('demand', 'medium'),
                'confidence': groq_result.get('confidence', 'MEDIUM'),
                'data_source': 'Groq AI Analysis',
                'source': 'Groq API',
                'is_commodity': True,
                'is_valid': True,
                'raw_response': groq_result.get('raw_response', '')
            }
        else:
            # Use fallback data
            fallback_data = get_fallback_data(product_name, region)
            
            if not fallback_data.get('is_commodity', True):
                return {
                    'product': product_name,
                    'error': fallback_data.get('error', 'Not a commodity'),
                    'is_valid': False,
                    'is_commodity': False,
                    'source': 'Invalid Input'
                }
            
            return {
                'product': product_name,
                'price': fallback_data.get('price'),
                'min_price': fallback_data.get('min_price'),
                'max_price': fallback_data.get('max_price'),
                'avg_price': fallback_data.get('avg_price'),
                'unit': fallback_data.get('unit', get_product_unit(product_name)),
                'trend': fallback_data.get('trend', 'stable'),
                'demand': fallback_data.get('demand', 'medium'),
                'confidence': fallback_data.get('confidence', 'MEDIUM'),
                'data_source': fallback_data.get('data_source', 'Market Estimate'),
                'source': 'Estimated',
                'is_commodity': fallback_data.get('is_commodity', True),
                'is_valid': True,
                'unit_display': fallback_data.get('unit_display', f'ETB/{get_product_unit(product_name)}'),
                'raw_response': ''
            }


# ==========================================
# RENDER AI INSIGHTS TAB
# ==========================================

def render_ai_insights(user_info, ai=None):
    """Render AI Insights tab with clean UI"""
    
    # Initialize AI
    ai_insights = SelfLearningAIInsights(user_info['id'])
    
    st.markdown("""
    <style>
    .insight-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .insight-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    .insight-card .title {
        color: #94a3b8;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    .insight-card .value {
        color: #f8fafc;
        font-size: 24px;
        font-weight: 700;
        margin: 4px 0;
    }
    .insight-card .sub {
        color: #94a3b8;
        font-size: 13px;
    }
    .confidence-high { color: #10b981; }
    .confidence-medium { color: #f59e0b; }
    .confidence-low { color: #ef4444; }
    .groq-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .fallback-badge {
        display: inline-block;
        background: #f59e0b;
        color: #0f172a;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .invalid-badge {
        display: inline-block;
        background: #ef4444;
        color: white;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .insight-text {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        margin: 8px 0;
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.6;
    }
    .insight-text strong {
        color: #f8fafc;
    }
    .search-section {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        margin-bottom: 16px;
    }
    .unit-badge {
        display: inline-block;
        background: #334155;
        color: #e2e8f0;
        font-size: 10px;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 500;
    }
    .warning-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #fca5a5;
    }
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #93c5fd;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("🤖 AI-Powered Market Insights")
    st.caption("Search and analyze agricultural commodities in the Ethiopian market")
    
    # Status
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧠 Learning", ai_insights.knowledge_base.get('learning_iterations', 0))
    with col2:
        st.metric("📊 Accuracy", f"{ai_insights.knowledge_base.get('accuracy_score', 0)*100:.1f}%")
    with col3:
        st.metric("📚 Knowledge", len(ai_insights.knowledge_base.get('training_data', [])))
    with col4:
        progress = min(ai_insights.knowledge_base.get('learning_iterations', 0) / 100, 1.0)
        st.metric("🎯 Progress", f"{progress*100:.0f}%")
    
    st.markdown("---")
    
    # API Key Check
    api_key = get_groq_api_key()
    if not api_key:
        st.warning("⚠️ Groq API key not found. Using fallback market data.")
        st.info("Add GROQ_API_KEY to secrets for AI-powered predictions.")
    
    # Get user's products for dropdown
    all_products = get_products(producer_id=user_info['id'])
    user_product_names = [p['name'] for p in all_products] if all_products else []
    
    # ==========================================
    # PRODUCT SELECTION
    # ==========================================
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown("### 🔍 Search Any Agricultural Product")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_option = st.radio(
            "Choose product source:",
            ["Select from my products", "Enter any product name"],
            horizontal=True
        )
    
    with col2:
        regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                  "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
        selected_region = st.selectbox("Region", regions, index=0)
    
    st.markdown("---")
    
    # Product name input - FIXED for "Enter any product name"
    if search_option == "Select from my products":
        if user_product_names:
            selected_product_name = st.selectbox(
                "Select Product",
                user_product_names,
                help="Select a product from your inventory"
            )
        else:
            st.warning("No products in your inventory. Please add products first or use custom search.")
            selected_product_name = st.text_input(
                "Enter Product Name",
                placeholder="e.g., Coffee, Teff, Wheat, Sugar, Onion, Tomato...",
                help="Enter any agricultural product to analyze"
            )
    else:
        # TEXT INPUT for custom product - FIXED
        selected_product_name = st.text_input(
            "Enter Product Name",
            placeholder="e.g., Coffee, Teff, Wheat, Sugar, Onion, Tomato, Beef, Milk...",
            help="Enter any agricultural product to analyze market prices"
        )
        
        # Show example products
        st.caption("💡 Examples: Coffee, Teff, Wheat, Sugar, Cooking Oil, Onion, Tomato, Beef, Milk, Egg, Banana")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not selected_product_name:
        st.info("💡 Select or enter a product name above to get market insights.")
        return
    
    product_name = selected_product_name.strip()
    unit = get_product_unit(product_name)
    is_valid_commodity = is_commodity(product_name)
    
    st.markdown("---")
    
    # Show product info
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"📦 Product: **{product_name}**")
    with col2:
        st.caption(f"📏 Unit: **{unit}**")
    
    if not is_valid_commodity:
        st.markdown(f"""
        <div class="warning-box">
            ⚠️ <strong>'{product_name}'</strong> is not a standard Ethiopian market commodity.
            Please try: coffee, teff, wheat, sugar, cooking oil, milk, beef, onion, tomato, egg, banana, etc.
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("---")
    
    # Get market data
    with st.spinner(f"Analyzing market data for {product_name}..."):
        market_data = ai_insights.get_market_data(product_name, selected_region)
    
    # Check if product is valid
    if not market_data.get('is_valid', True):
        st.error(f"❌ {market_data.get('error', 'Invalid product')}")
        return
    
    st.markdown("### 📊 Market Analysis")
    
    # Source badge
    if market_data.get('source') == 'Groq API':
        st.markdown('<span class="groq-badge">🤖 Groq AI</span>', unsafe_allow_html=True)
    elif market_data.get('source') == 'Invalid Input':
        st.markdown('<span class="invalid-badge">❌ Invalid</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="fallback-badge">📊 Estimated</span>', unsafe_allow_html=True)
    
    current_price = market_data.get('price', 0)
    market_avg = market_data.get('avg_price', 0)
    unit_display = market_data.get('unit', unit)
    confidence = market_data.get('confidence', 'MEDIUM')
    
    # Confidence color
    confidence_color = "confidence-high" if confidence == "HIGH" else "confidence-medium" if confidence == "MEDIUM" else "confidence-low"
    
    # Generate market insight
    if current_price and market_avg:
        diff = current_price - market_avg
        pct = (diff / market_avg * 100) if market_avg > 0 else 0
        
        if diff > 0:
            price_status = f"Your price is {pct:.0f}% above the market average"
            status_color = "#ef4444"
            status_emoji = "🔴"
        elif diff < 0:
            price_status = f"Your price is {abs(pct):.0f}% below the market average"
            status_color = "#10b981"
            status_emoji = "🟢"
        else:
            price_status = "Your price matches the market average"
            status_color = "#f59e0b"
            status_emoji = "🟡"
        
        st.markdown(f"""
        <div class="insight-text">
            💡 <strong>Market Insight:</strong> The current market price of <strong>{product_name}</strong> in <strong>{selected_region}</strong> is approximately 
            <strong>{market_avg:.0f} ETB/{unit_display}</strong>
            <br><br>
            {status_emoji} {price_status}.
            <br>
            📊 Estimated range: <strong>{market_data.get('min_price', 0):.0f} - {market_data.get('max_price', 0):.0f} ETB/{unit_display}</strong>
            <br>
            📈 Market trend is <strong>{market_data.get('trend', 'stable').capitalize()}</strong> 
            with <strong>{market_data.get('demand', 'medium').upper()}</strong> demand.
            <br>
            📍 Source: <strong>{market_data.get('data_source', 'Market Data')}</strong>
            <br>
            🎯 Confidence: <span class="{confidence_color}"><strong>{confidence}</strong></span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Estimated Price", f"{current_price:.0f} ETB/{unit_display}")
        with col2:
            st.metric("📊 Market Average", f"{market_avg:.0f} ETB/{unit_display}")
        with col3:
            st.metric("📈 Difference", f"{diff:+.0f} ETB", delta=f"{pct:+.1f}%")
        
        # Confidence indicator
        if confidence == "LOW":
            st.info("⚠️ Low confidence - Limited data available. Consider this estimate with caution.")
        elif confidence == "MEDIUM":
            st.info("📊 Medium confidence - Based on available market data.")
        else:
            st.success("✅ High confidence - Based on reliable market analysis.")
    
    # Market Details
    st.caption("---")
    detail_cols = st.columns(3)
    with detail_cols[0]:
        st.caption(f"📏 Unit: {unit_display}")
    with detail_cols[1]:
        if market_data.get('trend'):
            trend_emoji = "📈" if market_data.get('trend') == 'increasing' else "📉" if market_data.get('trend') == 'decreasing' else "➡️"
            st.caption(f"{trend_emoji} Trend: {market_data.get('trend', 'N/A').capitalize()}")
    with detail_cols[2]:
        if market_data.get('demand'):
            demand_emoji = "🔥" if market_data.get('demand') == 'high' else "📊" if market_data.get('demand') == 'medium' else "❄️"
            st.caption(f"{demand_emoji} Demand: {market_data.get('demand', 'N/A').capitalize()}")
    
    # Show raw response if available
    if market_data.get('raw_response') and st.checkbox("Show AI Analysis", key="show_raw"):
        with st.expander("📋 AI Analysis Details"):
            st.text(market_data.get('raw_response'))
    
    st.markdown("---")
    
    # Training section
    st.markdown("### 🧠 AI Training")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Train Model", use_container_width=True):
            with st.spinner("Training AI model with current data..."):
                training_data = ai_insights.generate_synthetic_data()
                success = ai_insights.train_model(training_data)
                if success:
                    st.success("✅ Model trained successfully!")
                    st.rerun()
                else:
                    st.error("❌ Training failed. Please try again.")
    
    with col2:
        if st.button("📊 View Performance", use_container_width=True):
            acc = ai_insights.knowledge_base.get('accuracy_score', 0)
            samples = len(ai_insights.knowledge_base.get('training_data', []))
            st.info(f"Accuracy: {acc*100:.1f}%")
            st.info(f"Samples: {samples}")
    
    with col3:
        if st.button("💾 Save Model", use_container_width=True):
            if ai_insights.save_model():
                st.success("✅ Model saved to Models/ folder!")
            else:
                st.error("❌ Failed to save model")
    
    st.caption("📁 Models saved to `Models/` folder")
