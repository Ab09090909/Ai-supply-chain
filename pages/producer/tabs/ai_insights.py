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
# GROQ API INTEGRATION
# ==========================================

def get_groq_api_key():
    """Get Groq API key from secrets"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("groq_api_key") or st.secrets.get("GROQ_KEY")
        return api_key
    except Exception as e:
        return None

def validate_product(product_name):
    """Validate product input - accepts all products"""
    if not product_name or len(product_name.strip()) < 2:
        return False, "Please enter a valid product name (at least 2 characters)"
    return True, "OK"

def query_groq_market_data(product_name, region="Addis Ababa"):
    """Query Groq API for any product - with better error handling and response parsing"""
    try:
        is_valid, msg = validate_product(product_name)
        if not is_valid:
            return {
                "success": False,
                "error": msg,
                "fallback_used": True
            }
        
        api_key = get_groq_api_key()
        if not api_key:
            return {
                "success": False,
                "error": "Groq API key not configured. Please add GROQ_API_KEY to secrets.",
                "fallback_used": True
            }

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Clear prompt asking for specific format
        prompt = f"""Analyze the market price for {product_name} in {region}, Ethiopia.

Provide your analysis in this exact format:

Unit: [the correct unit for this product - kg, liter, piece, unit, pair, meter, dozen, etc.]
Price: [number] ETB per [unit]
Range: [min] - [max] ETB per [unit]
Trend: [increasing/stable/decreasing]
Demand: [high/medium/low]
Confidence: [HIGH/MEDIUM/LOW]

Be realistic and specific for the Ethiopian market."""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a market analyst with knowledge of Ethiopian markets. Provide realistic price estimates in the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.1
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API Error {response.status_code}",
                "response_text": response.text[:200] if response.text else "No response",
                "fallback_used": True
            }
        
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content'].strip()
            
            # Parse response with multiple patterns
            unit_match = re.search(r'Unit:\s*(\w+)', content, re.IGNORECASE)
            price_match = re.search(r'Price:\s*([\d.]+)', content, re.IGNORECASE)
            range_match = re.search(r'Range:\s*([\d.]+)\s*-\s*([\d.]+)', content, re.IGNORECASE)
            trend_match = re.search(r'Trend:\s*(\w+)', content, re.IGNORECASE)
            demand_match = re.search(r'Demand:\s*(\w+)', content, re.IGNORECASE)
            confidence_match = re.search(r'Confidence:\s*(\w+)', content, re.IGNORECASE)
            
            # Get unit from Groq or default
            unit = unit_match.group(1).lower() if unit_match else "unit"
            
            result = {
                "success": True,
                "raw_response": content,
                "source": "Groq API",
                "unit": unit
            }
            
            if price_match:
                result["price"] = float(price_match.group(1))
            else:
                # Try to find any number if Price: format not found
                numbers = re.findall(r'([\d.]+)', content)
                if numbers:
                    result["price"] = float(numbers[0])
            
            if range_match:
                result["min_price"] = float(range_match.group(1))
                result["max_price"] = float(range_match.group(2))
            
            if trend_match:
                result["trend"] = trend_match.group(1).lower()
            else:
                result["trend"] = "stable"
            
            if demand_match:
                result["demand"] = demand_match.group(1).lower()
            else:
                result["demand"] = "medium"
            
            if confidence_match:
                result["confidence"] = confidence_match.group(1).upper()
            else:
                result["confidence"] = "MEDIUM"
            
            return result
        else:
            return {
                "success": False,
                "error": "Unexpected API response format",
                "raw_data": data,
                "fallback_used": True
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out", "fallback_used": True}
    except Exception as e:
        return {"success": False, "error": str(e), "fallback_used": True}

# ==========================================
# FALLBACK DATA FOR ANY PRODUCT
# ==========================================

def get_fallback_data(product_name, region="Addis Ababa"):
    """Get fallback data for any product"""
    return {
        'product': product_name,
        'price': None,
        'min_price': None,
        'max_price': None,
        'avg_price': None,
        'unit': 'unit',
        'trend': 'stable',
        'demand': 'medium',
        'data_source': 'Estimate',
        'source': 'Estimated',
        'is_fallback': True,
        'confidence': 'LOW',
        'unit_display': 'ETB/unit'
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
            {'name': 'wheat', 'price': 55, 'demand': 88, 'seasonal': 1.0},
            {'name': 'sugar', 'price': 65, 'demand': 85, 'seasonal': 0.9},
            {'name': 'oil', 'price': 150, 'demand': 92, 'seasonal': 1.0},
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
        
        # Validate product
        is_valid, msg = validate_product(product_name)
        if not is_valid:
            return {
                'product': product_name,
                'error': msg,
                'is_valid': False,
                'source': 'Validation Failed'
            }
        
        # Try Groq API first
        groq_result = query_groq_market_data(product_name, region)
        
        if groq_result.get('success') and groq_result.get('price'):
            return {
                'product': product_name,
                'price': groq_result.get('price'),
                'min_price': groq_result.get('min_price', groq_result.get('price') * 0.7),
                'max_price': groq_result.get('max_price', groq_result.get('price') * 1.3),
                'avg_price': groq_result.get('price'),
                'unit': groq_result.get('unit', 'unit'),
                'trend': groq_result.get('trend', 'stable'),
                'demand': groq_result.get('demand', 'medium'),
                'confidence': groq_result.get('confidence', 'MEDIUM'),
                'data_source': 'Groq AI Analysis',
                'source': 'Groq API',
                'is_valid': True,
                'raw_response': groq_result.get('raw_response', '')
            }
        else:
            # Use fallback data
            fallback_data = get_fallback_data(product_name, region)
            return {
                'product': product_name,
                'price': None,
                'min_price': None,
                'max_price': None,
                'avg_price': None,
                'unit': 'unit',
                'trend': 'stable',
                'demand': 'medium',
                'confidence': 'LOW',
                'data_source': 'Estimate - Groq API unavailable',
                'source': 'Estimated',
                'is_valid': True,
                'raw_response': '',
                'error': groq_result.get('error', 'Groq API returned no data')
            }


# ==========================================
# RENDER AI INSIGHTS TAB
# ==========================================

def render_ai_insights(user_info, ai=None):
    """Render AI Insights tab with Groq unit detection"""
    
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
    .result-box {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 20px;
        border: 2px solid #667eea;
        margin: 16px 0;
        text-align: center;
    }
    .result-box .price {
        font-size: 48px;
        font-weight: 700;
        color: #10b981;
    }
    .result-box .unit {
        font-size: 20px;
        color: #94a3b8;
    }
    .result-box .label {
        color: #94a3b8;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("🤖 AI-Powered Market Insights")
    st.caption("Search and analyze any product in the Ethiopian market")
    
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
        st.warning("⚠️ Groq API key not found. Using fallback data.")
        st.info("Add GROQ_API_KEY to secrets for AI-powered predictions.")
    
    # Get user's products for dropdown
    all_products = get_products(producer_id=user_info['id'])
    user_product_names = [p['name'] for p in all_products] if all_products else []
    
    # ==========================================
    # PRODUCT SELECTION
    # ==========================================
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown("### 🔍 Search Any Product")
    
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
    
    # Product name input
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
                placeholder="e.g., Coffee, Teff, Car, Phone...",
                help="Enter any product to analyze"
            )
    else:
        selected_product_name = st.text_input(
            "Enter Product Name",
            placeholder="e.g., Coffee, Teff, Car, Phone, Laptop, Onion, Tomato, Beef, Milk, Egg...",
            help="Enter any product to analyze market prices"
        )
        
        st.caption("💡 Examples: Coffee, Teff, Car, Phone, Laptop, Onion, Tomato, Beef, Milk, Egg, Banana, Shoes, TV")
    
    # Quick search buttons
    st.markdown("#### Quick Search")
    quick_products = ["Coffee", "Teff", "Car", "Phone", "Onion", "Tomato", "Beef", "Milk"]
    quick_cols = st.columns(4)
    for i, product in enumerate(quick_products):
        with quick_cols[i % 4]:
            if st.button(f"🔍 {product}", use_container_width=True):
                st.session_state.quick_product = product
                st.rerun()
    
    # Check for quick product
    if 'quick_product' in st.session_state and st.session_state.quick_product:
        selected_product_name = st.session_state.quick_product
        st.session_state.quick_product = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not selected_product_name:
        st.info("💡 Select or enter a product name above to get market insights.")
        return
    
    product_name = selected_product_name.strip()
    
    st.markdown("---")
    
    # Show loading state while fetching data
    with st.spinner(f"🔍 Analyzing market data for {product_name} in {selected_region}..."):
        market_data = ai_insights.get_market_data(product_name, selected_region)
    
    # Check if product is valid
    if not market_data.get('is_valid', True):
        st.error(f"❌ {market_data.get('error', 'Invalid product')}")
        return
    
    st.markdown("### 📊 Market Analysis Results")
    st.caption(f"📍 {product_name} in {selected_region}")
    
    # Display results prominently
    if market_data.get('source') == 'Groq API':
        st.markdown('<span class="groq-badge">🤖 Powered by Groq AI</span>', unsafe_allow_html=True)
        
        price = market_data.get('price')
        unit = market_data.get('unit', 'unit')
        min_price = market_data.get('min_price')
        max_price = market_data.get('max_price')
        trend = market_data.get('trend', 'stable')
        demand = market_data.get('demand', 'medium')
        confidence = market_data.get('confidence', 'MEDIUM')
        
        # Display price prominently
        if price:
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Estimated Market Price</div>
                <div class="price">{price:,.0f}</div>
                <div class="unit">ETB per {unit}</div>
                <div style="margin-top: 12px; color: #94a3b8; font-size: 14px;">
                    Range: {min_price:,.0f} - {max_price:,.0f} ETB/{unit}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Market details
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            trend_emoji = "📈" if trend == 'increasing' else "📉" if trend == 'decreasing' else "➡️"
            st.metric("📈 Trend", f"{trend_emoji} {trend.capitalize()}")
        with col2:
            demand_emoji = "🔥" if demand == 'high' else "📊" if demand == 'medium' else "❄️"
            st.metric("📊 Demand", f"{demand_emoji} {demand.capitalize()}")
        with col3:
            confidence_color = "confidence-high" if confidence == "HIGH" else "confidence-medium" if confidence == "MEDIUM" else "confidence-low"
            st.metric("🎯 Confidence", f"<span class='{confidence_color}'>{confidence}</span>", unsafe_allow_html=True)
        with col4:
            st.metric("📏 Unit", unit.capitalize())
        
        # AI Analysis
        if market_data.get('raw_response'):
            with st.expander("📋 View AI Analysis Details", expanded=False):
                st.text(market_data.get('raw_response'))
        
        # Explanation
        st.markdown("---")
        st.markdown("#### 💡 Understanding the Analysis")
        st.caption(f"""
        - **Price**: Estimated current market price for {product_name}
        - **Range**: Typical price range found in the market
        - **Trend**: Whether prices are going up, down, or stable
        - **Demand**: Current market demand level
        - **Confidence**: How reliable the estimate is
        """)
        
        if confidence == "LOW":
            st.warning("⚠️ Low confidence - Limited data available. Please verify with local sources.")
        elif confidence == "MEDIUM":
            st.info("📊 Medium confidence - Based on available market data.")
        else:
            st.success("✅ High confidence - Based on reliable market data.")
            
    else:
        # Fallback - show error message
        st.markdown('<span class="fallback-badge">📊 Estimated Data</span>', unsafe_allow_html=True)
        st.warning(f"⚠️ Could not fetch AI analysis for {product_name}")
        
        error_msg = market_data.get('error', 'No data available')
        st.info(f"💡 {error_msg}")
        
        st.markdown("""
        #### 💡 Tips:
        - Make sure your GROQ_API_KEY is set in Streamlit secrets
        - Check your internet connection
        - Try a different product name
        - The AI works best with common Ethiopian market products
        """)
        
        # Show raw response if available
        if market_data.get('raw_response'):
            with st.expander("📋 View Raw Response", expanded=False):
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
