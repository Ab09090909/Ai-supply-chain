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
    """Validate product input"""
    if not product_name or len(product_name.strip()) < 2:
        return False, "Please enter a valid product name (at least 2 characters)"
    return True, "OK"

def query_groq_market_data(product_name, region="Addis Ababa"):
    """Query Groq API for detailed price breakdown"""
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
                "error": "Groq API key not configured.",
                "fallback_used": True
            }

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt for detailed price breakdown
        prompt = f"""Analyze the market for {product_name} in {region}, Ethiopia.

Provide a DETAILED PRICE BREAKDOWN by grade, quality, model, or variant.

Format your response exactly like this:

Unit: [kg/liter/piece/unit]
Base Price: [number] ETB per [unit]
Price Range: [min] - [max] ETB per [unit]
Trend: [increasing/stable/decreasing]
Demand: [high/medium/low]
Confidence: [HIGH/MEDIUM/LOW]
Description: [2-3 sentences explaining the market situation]

PRICE BREAKDOWN BY GRADE:
- Grade A / Premium / High Quality: [price] ETB per [unit]
- Grade B / Standard / Medium Quality: [price] ETB per [unit]
- Grade C / Basic / Low Quality: [price] ETB per [unit]

PRICE BREAKDOWN BY VARIANT (if applicable):
- [Variant name 1]: [price] ETB per [unit]
- [Variant name 2]: [price] ETB per [unit]
- [Variant name 3]: [price] ETB per [unit]

Make the breakdown realistic for Ethiopian market conditions.
If the product doesn't have grades, use price tiers based on quality or size."""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a market analyst with knowledge of Ethiopian markets. Provide detailed price breakdowns by grade and quality."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 600,
            "temperature": 0.1
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API Error {response.status_code}",
                "fallback_used": True
            }
        
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content'].strip()
            
            # Parse main fields
            unit_match = re.search(r'Unit:\s*(\w+)', content, re.IGNORECASE)
            price_match = re.search(r'Base Price:\s*([\d.]+)', content, re.IGNORECASE)
            range_match = re.search(r'Price Range:\s*([\d.]+)\s*-\s*([\d.]+)', content, re.IGNORECASE)
            trend_match = re.search(r'Trend:\s*(\w+)', content, re.IGNORECASE)
            demand_match = re.search(r'Demand:\s*(\w+)', content, re.IGNORECASE)
            confidence_match = re.search(r'Confidence:\s*(\w+)', content, re.IGNORECASE)
            description_match = re.search(r'Description:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
            
            # Parse price breakdown by grade
            grade_pattern = r'Grade\s*([A-C])\s*/\s*([^:]+):?\s*([\d.]+)\s*ETB'
            grade_matches = re.findall(grade_pattern, content, re.IGNORECASE)
            
            # Parse price breakdown by variant
            variant_pattern = r'-\s*([^:]+):?\s*([\d.]+)\s*ETB'
            variant_matches = re.findall(variant_pattern, content, re.IGNORECASE)
            
            # If no grade matches found, try alternative pattern
            if not grade_matches:
                grade_pattern2 = r'([A-C])\s*/\s*([^:]+):?\s*([\d.]+)\s*ETB'
                grade_matches = re.findall(grade_pattern2, content, re.IGNORECASE)
            
            # Filter out variant matches that are actually grades
            grade_variants = [g[1].strip() for g in grade_matches]
            variant_matches = [(v[0].strip(), float(v[1])) for v in variant_matches if v[0].strip() not in grade_variants]
            
            # Build grade breakdown
            grade_breakdown = []
            if grade_matches:
                for grade in grade_matches:
                    grade_breakdown.append({
                        'grade': grade[0].upper(),
                        'name': grade[1].strip(),
                        'price': float(grade[2])
                    })
            
            # Build variant breakdown
            variant_breakdown = []
            if variant_matches:
                for variant in variant_matches[:5]:  # Limit to 5 variants
                    variant_breakdown.append({
                        'name': variant[0].strip(),
                        'price': variant[1]
                    })
            
            # Get values
            unit = unit_match.group(1).lower() if unit_match else "unit"
            base_price = float(price_match.group(1)) if price_match else None
            description = description_match.group(1).strip() if description_match else "Market analysis based on available data."
            
            result = {
                "success": True,
                "raw_response": content,
                "source": "Groq API",
                "unit": unit,
                "base_price": base_price,
                "description": description,
                "grade_breakdown": grade_breakdown,
                "variant_breakdown": variant_breakdown
            }
            
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
                "fallback_used": True
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out", "fallback_used": True}
    except Exception as e:
        return {"success": False, "error": str(e), "fallback_used": True}

# ==========================================
# FALLBACK DATA
# ==========================================

def get_fallback_data(product_name, region="Addis Ababa"):
    """Get fallback data with sample breakdown"""
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
        'description': 'Limited data available for this product.',
        'grade_breakdown': [],
        'variant_breakdown': [],
        'is_fallback': True
    }

# ==========================================
# SELF-LEARNING AI SYSTEM
# ==========================================

class SelfLearningAIInsights:
    """Self-learning AI system"""
    
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
        except:
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
        try:
            with open(f"{self.data_dir}/ai_knowledge_{self.user_id}.json", 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
        except:
            pass
    
    def load_or_train_model(self):
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
        except:
            return False
    
    def train_model(self, training_data):
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
        except:
            return False
    
    def generate_synthetic_data(self):
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
        try:
            model_path = f"{self.models_dir}/ai_model_{self.user_id}.pkl"
            scaler_path = f"{self.models_dir}/ai_scaler_{self.user_id}.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            return True
        except:
            return False
    
    def get_market_data(self, product_name, region="Addis Ababa"):
        is_valid, msg = validate_product(product_name)
        if not is_valid:
            return {
                'product': product_name,
                'error': msg,
                'is_valid': False
            }
        
        groq_result = query_groq_market_data(product_name, region)
        
        if groq_result.get('success') and groq_result.get('base_price'):
            return {
                'product': product_name,
                'base_price': groq_result.get('base_price'),
                'min_price': groq_result.get('min_price', groq_result.get('base_price') * 0.7),
                'max_price': groq_result.get('max_price', groq_result.get('base_price') * 1.3),
                'unit': groq_result.get('unit', 'unit'),
                'trend': groq_result.get('trend', 'stable'),
                'demand': groq_result.get('demand', 'medium'),
                'confidence': groq_result.get('confidence', 'MEDIUM'),
                'description': groq_result.get('description', ''),
                'grade_breakdown': groq_result.get('grade_breakdown', []),
                'variant_breakdown': groq_result.get('variant_breakdown', []),
                'source': 'Groq API',
                'is_valid': True,
                'raw_response': groq_result.get('raw_response', '')
            }
        else:
            fallback_data = get_fallback_data(product_name, region)
            return {
                'product': product_name,
                'base_price': None,
                'min_price': None,
                'max_price': None,
                'unit': 'unit',
                'trend': 'stable',
                'demand': 'medium',
                'confidence': 'LOW',
                'description': 'Limited data available.',
                'grade_breakdown': [],
                'variant_breakdown': [],
                'source': 'Estimated',
                'is_valid': True,
                'raw_response': '',
                'error': groq_result.get('error', 'No data available')
            }


# ==========================================
# RENDER AI INSIGHTS TAB
# ==========================================

def render_ai_insights(user_info, ai=None):
    """Render AI Insights tab with detailed price breakdown"""
    
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
    .price-breakdown {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        margin: 8px 0;
    }
    .price-breakdown .item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1e293b;
    }
    .price-breakdown .item:last-child {
        border-bottom: none;
    }
    .price-breakdown .label {
        color: #94a3b8;
    }
    .price-breakdown .price {
        color: #10b981;
        font-weight: 600;
    }
    .price-breakdown .grade-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 8px;
    }
    .grade-a { background: #10b981; color: #0f172a; }
    .grade-b { background: #f59e0b; color: #0f172a; }
    .grade-c { background: #ef4444; color: white; }
    .description-box {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        margin: 12px 0;
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.7;
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
    st.caption("Search and analyze any product with detailed price breakdown by grade and quality")
    
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
    
    # Get user's products
    all_products = get_products(producer_id=user_info['id'])
    user_product_names = [p['name'] for p in all_products] if all_products else []
    
    # Product Selection
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
    
    if search_option == "Select from my products":
        if user_product_names:
            selected_product_name = st.selectbox("Select Product", user_product_names)
        else:
            st.warning("No products in your inventory.")
            selected_product_name = st.text_input(
                "Enter Product Name",
                placeholder="e.g., Coffee, Teff, Car, Phone..."
            )
    else:
        selected_product_name = st.text_input(
            "Enter Product Name",
            placeholder="e.g., Coffee, Teff, Car, Phone, Laptop, Onion, Tomato, Beef, Milk, Egg...",
            help="Enter any product to analyze market prices"
        )
        st.caption("💡 Examples: Coffee, Teff, Car, Phone, Laptop, Onion, Tomato, Beef, Milk, Egg, Banana, Shoes, TV")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not selected_product_name:
        st.info("💡 Select or enter a product name above to get market insights.")
        return
    
    product_name = selected_product_name.strip()
    st.markdown("---")
    
    # Fetch data
    with st.spinner(f"🔍 Analyzing market data for {product_name} in {selected_region}..."):
        market_data = ai_insights.get_market_data(product_name, selected_region)
    
    if not market_data.get('is_valid', True):
        st.error(f"❌ {market_data.get('error', 'Invalid product')}")
        return
    
    st.markdown("### 📊 Market Analysis Results")
    st.caption(f"📍 {product_name} in {selected_region}")
    
    if market_data.get('source') == 'Groq API':
        st.markdown('<span class="groq-badge">🤖 Powered by Groq AI</span>', unsafe_allow_html=True)
        
        base_price = market_data.get('base_price')
        unit = market_data.get('unit', 'unit')
        min_price = market_data.get('min_price')
        max_price = market_data.get('max_price')
        trend = market_data.get('trend', 'stable')
        demand = market_data.get('demand', 'medium')
        confidence = market_data.get('confidence', 'MEDIUM')
        description = market_data.get('description', '')
        grade_breakdown = market_data.get('grade_breakdown', [])
        variant_breakdown = market_data.get('variant_breakdown', [])
        
        # Base Price Display
        if base_price:
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Base Market Price</div>
                <div class="price">{base_price:,.0f}</div>
                <div class="unit">ETB per {unit}</div>
                <div style="margin-top: 12px; color: #94a3b8; font-size: 14px;">
                    Range: {min_price:,.0f} - {max_price:,.0f} ETB/{unit}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Market Details
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            trend_emoji = "📈" if trend == 'increasing' else "📉" if trend == 'decreasing' else "➡️"
            st.metric("📈 Trend", f"{trend_emoji} {trend.capitalize()}")
        with col2:
            demand_emoji = "🔥" if demand == 'high' else "📊" if demand == 'medium' else "❄️"
            st.metric("📊 Demand", f"{demand_emoji} {demand.capitalize()}")
        with col3:
            st.metric("🎯 Confidence", confidence)
            color = "#10b981" if confidence == "HIGH" else "#f59e0b" if confidence == "MEDIUM" else "#ef4444"
            st.caption(f"<span style='color:{color}'>{confidence}</span>", unsafe_allow_html=True)
        with col4:
            st.metric("📏 Unit", unit.capitalize())
        
        # Description
        if description:
            st.markdown("#### 📝 Market Description")
            st.markdown(f"""
            <div class="description-box">
                {description}
            </div>
            """, unsafe_allow_html=True)
        
        # Price Breakdown by Grade
        if grade_breakdown:
            st.markdown("#### 📊 Price Breakdown by Grade")
            st.markdown('<div class="price-breakdown">', unsafe_allow_html=True)
            
            for item in grade_breakdown:
                grade_class = f"grade-{item['grade'].lower()}" if item['grade'] in ['A', 'B', 'C'] else "grade-b"
                st.markdown(f"""
                <div class="item">
                    <div>
                        <span class="grade-badge {grade_class}">{item['grade']}</span>
                        <span class="label">{item['name']}</span>
                    </div>
                    <span class="price">{item['price']:,.0f} ETB/{unit}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Price Breakdown by Variant
        if variant_breakdown:
            st.markdown("#### 🏷️ Price Breakdown by Variant/Model")
            st.markdown('<div class="price-breakdown">', unsafe_allow_html=True)
            
            for item in variant_breakdown:
                st.markdown(f"""
                <div class="item">
                    <span class="label">{item['name']}</span>
                    <span class="price">{item['price']:,.0f} ETB/{unit}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # If no breakdown available
        if not grade_breakdown and not variant_breakdown:
            st.info("💡 No detailed price breakdown available for this product.")
        
        # Raw response
        if market_data.get('raw_response'):
            with st.expander("📋 View AI Analysis Details", expanded=False):
                st.text(market_data.get('raw_response'))
        
        # Confidence warning
        if confidence == "LOW":
            st.warning("⚠️ Low confidence - Limited data available. Please verify with local sources.")
        elif confidence == "MEDIUM":
            st.info("📊 Medium confidence - Based on available market data.")
        else:
            st.success("✅ High confidence - Based on reliable market analysis.")
            
    else:
        # Fallback
        st.markdown('<span class="fallback-badge">📊 Estimated Data</span>', unsafe_allow_html=True)
        st.warning(f"⚠️ Could not fetch AI analysis for {product_name}")
        
        if market_data.get('error'):
            st.info(f"💡 {market_data.get('error')}")
        
        st.markdown("""
        #### 💡 Tips:
        - Make sure your GROQ_API_KEY is set in Streamlit secrets
        - Check your internet connection
        - Try a different product name
        """)
        
        if market_data.get('raw_response'):
            with st.expander("📋 View Raw Response", expanded=False):
                st.text(market_data.get('raw_response'))
    
    st.markdown("---")
    
    # Training
    st.markdown("### 🧠 AI Training")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Train Model", use_container_width=True):
            with st.spinner("Training AI model..."):
                training_data = ai_insights.generate_synthetic_data()
                success = ai_insights.train_model(training_data)
                if success:
                    st.success("✅ Model trained successfully!")
                    st.rerun()
                else:
                    st.error("❌ Training failed.")
    
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
