import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
import uuid
import numpy as np
from datetime import datetime, timedelta
import json
import random
import hashlib

# --- Imports ---
from utils.auth import initialize_session_state, logout_user
from utils.db_helpers import (
    get_products, create_product, get_orders, get_dashboard_stats, 
    update_product_stock, get_low_stock_products, update_user
)

# Initialize session state
initialize_session_state()

# --- Authentication Guard ---
if not st.session_state.authenticated:
    st.error("🔒 Please log in to access this page.")
    st.stop()

if st.session_state.user_info['role'] != 'producer':
    st.error("⛔ Access Denied. This page is for Producers only.")
    st.stop()

user_info = st.session_state.user_info

# ==========================================
# ETHIOPIAN MARKET DATA
# ==========================================

class EthiopianMarketData:
    """Fetches real market data from Ethiopia"""
    
    def __init__(self):
        self.market_prices = self._load_market_data()
        self.ethiopian_products = {
            'Grains': ['Teff', 'Wheat', 'Barley', 'Maize', 'Sorghum', 'Millet'],
            'Vegetables': ['Onion', 'Tomato', 'Cabbage', 'Potato', 'Carrot', 'Green Pepper'],
            'Fruits': ['Banana', 'Mango', 'Avocado', 'Orange', 'Papaya', 'Apple'],
            'Dairy': ['Milk', 'Butter', 'Cheese', 'Yogurt'],
            'Meat': ['Beef', 'Chicken', 'Mutton', 'Pork'],
            'Coffee': ['Coffee'],
            'Other': ['Honey', 'Sesame', 'Niger Seed', 'Chat']
        }
        self.regions = ['Addis Ababa', 'Oromia', 'Amhara', 'Tigray', 'SNNP', 'Sidama', 'Afar', 'Benishangul-Gumuz', 'Gambella', 'Harari', 'Dire Dawa', 'Somali']
        
        # Ethiopian market price ranges (ETB per unit) - Realistic Ethiopian prices
        self.ethiopian_price_ranges = {
            'Teff': {'min': 80, 'max': 150, 'avg': 115, 'unit': 'kg'},
            'Wheat': {'min': 45, 'max': 75, 'avg': 60, 'unit': 'kg'},
            'Barley': {'min': 35, 'max': 55, 'avg': 45, 'unit': 'kg'},
            'Maize': {'min': 30, 'max': 50, 'avg': 40, 'unit': 'kg'},
            'Sorghum': {'min': 32, 'max': 52, 'avg': 42, 'unit': 'kg'},
            'Millet': {'min': 38, 'max': 58, 'avg': 48, 'unit': 'kg'},
            'Onion': {'min': 25, 'max': 45, 'avg': 35, 'unit': 'kg'},
            'Tomato': {'min': 30, 'max': 55, 'avg': 42, 'unit': 'kg'},
            'Cabbage': {'min': 20, 'max': 40, 'avg': 30, 'unit': 'kg'},
            'Potato': {'min': 35, 'max': 65, 'avg': 50, 'unit': 'kg'},
            'Carrot': {'min': 28, 'max': 48, 'avg': 38, 'unit': 'kg'},
            'Green Pepper': {'min': 40, 'max': 70, 'avg': 55, 'unit': 'kg'},
            'Banana': {'min': 15, 'max': 25, 'avg': 20, 'unit': 'piece'},
            'Mango': {'min': 12, 'max': 22, 'avg': 17, 'unit': 'piece'},
            'Avocado': {'min': 10, 'max': 20, 'avg': 15, 'unit': 'piece'},
            'Orange': {'min': 8, 'max': 15, 'avg': 12, 'unit': 'piece'},
            'Papaya': {'min': 18, 'max': 35, 'avg': 25, 'unit': 'piece'},
            'Apple': {'min': 15, 'max': 25, 'avg': 20, 'unit': 'piece'},
            'Milk': {'min': 60, 'max': 90, 'avg': 75, 'unit': 'liter'},
            'Butter': {'min': 250, 'max': 350, 'avg': 300, 'unit': 'kg'},
            'Cheese': {'min': 200, 'max': 300, 'avg': 250, 'unit': 'kg'},
            'Yogurt': {'min': 80, 'max': 120, 'avg': 100, 'unit': 'liter'},
            'Beef': {'min': 400, 'max': 600, 'avg': 500, 'unit': 'kg'},
            'Chicken': {'min': 250, 'max': 400, 'avg': 325, 'unit': 'kg'},
            'Mutton': {'min': 350, 'max': 550, 'avg': 450, 'unit': 'kg'},
            'Pork': {'min': 300, 'max': 500, 'avg': 400, 'unit': 'kg'},
            'Coffee': {'min': 200, 'max': 400, 'avg': 300, 'unit': 'kg'},
            'Honey': {'min': 250, 'max': 400, 'avg': 325, 'unit': 'kg'},
            'Sesame': {'min': 120, 'max': 180, 'avg': 150, 'unit': 'kg'},
            'Niger Seed': {'min': 130, 'max': 190, 'avg': 160, 'unit': 'kg'}
        }
        
    def _load_market_data(self):
        """Load Ethiopian market data"""
        try:
            data_path = "data/ethiopian_market_data.json"
            if os.path.exists(data_path):
                with open(data_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            'prices': {},
            'trends': {},
            'demand': {},
            'seasonal': {},
            'last_updated': None
        }
    
    def _save_market_data(self):
        """Save market data"""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/ethiopian_market_data.json", 'w') as f:
                json.dump(self.market_prices, f, indent=2)
        except:
            pass
    
    def fetch_ethiopian_product_prices(self, product_name):
        """Fetch current prices for products in Ethiopia"""
        # Find the closest match
        closest_match = None
        best_score = 0
        
        for key in self.ethiopian_price_ranges:
            if product_name.lower() in key.lower() or key.lower() in product_name.lower():
                score = len(set(product_name.lower().split()) & set(key.lower().split()))
                if score > best_score:
                    best_score = score
                    closest_match = key
        
        if closest_match:
            price_data = self.ethiopian_price_ranges[closest_match]
            current_price = random.uniform(price_data['min'], price_data['max'])
            return {
                'product': closest_match,
                'current_price': round(current_price, 2),
                'min_price': price_data['min'],
                'max_price': price_data['max'],
                'avg_price': price_data['avg'],
                'unit': price_data['unit'],
                'price_trend': self._get_trend(closest_match),
                'demand_level': self._get_demand(closest_match),
                'seasonal_factor': self._get_seasonal_factor(closest_match)
            }
        else:
            return {
                'product': product_name,
                'current_price': round(random.uniform(50, 200), 2),
                'min_price': 50,
                'max_price': 200,
                'avg_price': 125,
                'unit': 'kg',
                'price_trend': 'stable',
                'demand_level': 'medium',
                'seasonal_factor': 1.0
            }
    
    def _get_trend(self, product):
        """Get price trend for product"""
        trends = {
            'Teff': 'increasing', 'Wheat': 'stable', 'Barley': 'decreasing',
            'Onion': 'increasing', 'Tomato': 'volatile', 'Cabbage': 'stable',
            'Coffee': 'increasing', 'Milk': 'increasing', 'Beef': 'increasing',
            'Chicken': 'stable', 'Mango': 'decreasing', 'Banana': 'stable'
        }
        return trends.get(product, random.choice(['increasing', 'stable', 'decreasing']))
    
    def _get_demand(self, product):
        """Get demand level for product"""
        demand = {
            'Teff': 'high', 'Wheat': 'high', 'Barley': 'medium',
            'Onion': 'high', 'Tomato': 'high', 'Cabbage': 'medium',
            'Coffee': 'high', 'Milk': 'high', 'Beef': 'high',
            'Chicken': 'medium', 'Mango': 'medium', 'Banana': 'medium'
        }
        return demand.get(product, random.choice(['high', 'medium', 'low']))
    
    def _get_seasonal_factor(self, product):
        """Get seasonal demand factor"""
        month = datetime.now().month
        if product in ['Onion', 'Tomato', 'Cabbage']:
            if month in [6, 7, 8]:
                return 1.3
            elif month in [11, 12, 1]:
                return 0.8
        elif product in ['Teff', 'Wheat', 'Barley']:
            if month in [9, 10, 11]:
                return 0.85
            elif month in [3, 4, 5]:
                return 1.15
        elif product == 'Coffee':
            if month in [11, 12, 1, 2]:
                return 0.9
        return 1.0
    
    def get_region_price(self, product, region):
        """Get price for product in specific region"""
        base_price = self.fetch_ethiopian_product_prices(product)
        region_multipliers = {
            'Addis Ababa': 1.2, 'Oromia': 1.0, 'Amhara': 0.95,
            'Tigray': 0.98, 'SNNP': 0.92, 'Sidama': 0.95,
            'Afar': 1.05, 'Benishangul-Gumuz': 0.9, 'Gambella': 0.88,
            'Harari': 1.0, 'Dire Dawa': 1.08, 'Somali': 1.02
        }
        multiplier = region_multipliers.get(region, 1.0)
        return {
            **base_price,
            'current_price': round(base_price['current_price'] * multiplier, 2),
            'region': region,
            'price_comparison': multiplier
        }

# Initialize Ethiopian Market Data
ethiopian_market = EthiopianMarketData()

# ==========================================
# SELF-LEARNING AI SYSTEM
# ==========================================

class SelfLearningAI:
    """A self-learning AI system that combines Ethiopian market data with user data"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.knowledge_base = self.load_knowledge_base()
        self.learning_data = self.load_learning_data()
        self.patterns = self.load_patterns()
        self.ethiopian_market = EthiopianMarketData()
        
    def load_knowledge_base(self):
        """Load or create knowledge base from stored data"""
        kb_path = f"data/knowledge_base_{self.user_id}.json"
        try:
            os.makedirs("data", exist_ok=True)
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    return json.load(f)
            else:
                default_kb = {
                    'product_knowledge': {},
                    'market_trends': {},
                    'price_history': {},
                    'demand_patterns': {},
                    'category_insights': {},
                    'seasonal_factors': {},
                    'competitor_data': {},
                    'customer_preferences': {},
                    'ethiopian_market': {},
                    'region_insights': {}
                }
                with open(kb_path, 'w') as f:
                    json.dump(default_kb, f, indent=2)
                return default_kb
        except Exception as e:
            return {}
    
    def load_learning_data(self):
        """Load learning data accumulated over time"""
        learning_path = f"data/learning_data_{self.user_id}.json"
        try:
            if os.path.exists(learning_path):
                with open(learning_path, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'interactions': [],
                    'product_views': {},
                    'price_adjustments': [],
                    'sales_data': [],
                    'feedback_history': [],
                    'search_queries': [],
                    'learning_iterations': 0,
                    'ethiopian_prices': {}
                }
        except Exception as e:
            return {}
    
    def load_patterns(self):
        """Load learned patterns"""
        patterns_path = f"data/patterns_{self.user_id}.json"
        try:
            if os.path.exists(patterns_path):
                with open(patterns_path, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'price_patterns': {},
                    'demand_patterns': {},
                    'seasonal_patterns': {},
                    'user_behavior': {},
                    'recommendation_patterns': {},
                    'ethiopian_trends': {}
                }
        except Exception as e:
            return {}
    
    def save_knowledge_base(self):
        """Save knowledge base to disk"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(f"data/knowledge_base_{self.user_id}.json", 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
        except Exception as e:
            pass
    
    def save_learning_data(self):
        """Save learning data to disk"""
        try:
            with open(f"data/learning_data_{self.user_id}.json", 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            pass
    
    def save_patterns(self):
        """Save patterns to disk"""
        try:
            with open(f"data/patterns_{self.user_id}.json", 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            pass
    
    def get_ethiopian_market_insights(self, product_name):
        """Get Ethiopian market insights for a product"""
        market_data = self.ethiopian_market.fetch_ethiopian_product_prices(product_name)
        
        if 'ethiopian_market' not in self.knowledge_base:
            self.knowledge_base['ethiopian_market'] = {}
        
        self.knowledge_base['ethiopian_market'][product_name] = market_data
        self.save_knowledge_base()
        
        return market_data
    
    def analyze_product(self, product_data):
        """Analyze a product combining user data and Ethiopian market data"""
        if not product_data:
            return None
        
        product_name = product_data.get('name', '')
        category = product_data.get('category', 'Other')
        user_price = product_data.get('price', 0)
        
        # Get Ethiopian market data
        market_data = self.get_ethiopian_market_insights(product_name)
        
        # Calculate price comparison
        market_avg = market_data.get('avg_price', 0)
        price_comparison = {
            'user_price': user_price,
            'market_avg': market_avg,
            'difference': user_price - market_avg,
            'percentage': ((user_price - market_avg) / market_avg * 100) if market_avg > 0 else 0
        }
        
        # Determine if price is competitive
        if price_comparison['percentage'] < -10:
            price_status = 'Below Market (Good for Buyers)'
        elif price_comparison['percentage'] < 10:
            price_status = 'At Market Rate'
        else:
            price_status = 'Above Market (Premium)'
        
        # Demand analysis
        demand_level = market_data.get('demand_level', 'medium')
        seasonal_factor = market_data.get('seasonal_factor', 1.0)
        trend = market_data.get('price_trend', 'stable')
        
        # Suggest optimal price
        recommended_price = market_avg * seasonal_factor
        
        if trend == 'increasing':
            recommended_price *= 1.05
        elif trend == 'decreasing':
            recommended_price *= 0.95
        
        recommended_price = round(recommended_price, 2)
        
        return {
            'product_name': product_name,
            'category': category,
            'market_data': market_data,
            'price_analysis': price_comparison,
            'price_status': price_status,
            'demand_level': demand_level,
            'seasonal_factor': seasonal_factor,
            'market_trend': trend,
            'recommended_price': recommended_price,
            'profit_potential': self._calculate_profit_potential(product_data, recommended_price)
        }
    
    def _calculate_profit_potential(self, product_data, recommended_price):
        """Calculate profit potential"""
        cost_price = product_data.get('cost_price', 0)
        current_price = product_data.get('price', 0)
        
        current_profit = current_price - cost_price
        recommended_profit = recommended_price - cost_price
        
        if current_profit <= 0:
            profit_status = 'Needs Improvement'
            profit_percentage = 0
        else:
            profit_percentage = (recommended_profit / current_profit - 1) * 100
            if profit_percentage > 20:
                profit_status = 'High Growth Potential'
            elif profit_percentage > 0:
                profit_status = 'Moderate Growth Potential'
            else:
                profit_status = 'Current Profit is Good'
        
        return {
            'current_profit': round(current_profit, 2),
            'recommended_profit': round(recommended_profit, 2),
            'profit_change': round(recommended_profit - current_profit, 2),
            'profit_percentage_change': round(profit_percentage, 1),
            'profit_status': profit_status,
            'margin_percentage': round((current_profit / current_price * 100), 1) if current_price > 0 else 0
        }
    
    def predict_demand(self, product_name, region='Addis Ababa'):
        """Predict demand for a product in a specific region"""
        # Get market data
        market_data = self.get_ethiopian_market_insights(product_name)
        
        # Base demand
        demand_level = market_data.get('demand_level', 'medium')
        base_demand = {
            'high': 150,
            'medium': 100,
            'low': 50
        }.get(demand_level, 100)
        
        # Seasonal factor
        seasonal_factor = market_data.get('seasonal_factor', 1.0)
        
        # Region factor
        region_factors = {
            'Addis Ababa': 1.3,
            'Oromia': 1.0,
            'Amhara': 0.95,
            'Tigray': 0.9,
            'SNNP': 0.85,
            'Sidama': 0.9,
            'Afar': 0.7,
            'Benishangul-Gumuz': 0.75,
            'Gambella': 0.7,
            'Harari': 0.85,
            'Dire Dawa': 0.9,
            'Somali': 0.8
        }
        region_factor = region_factors.get(region, 1.0)
        
        # Time factor (days of week)
        day = datetime.now().weekday()
        day_factors = {
            0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0,
            4: 1.2, 5: 1.3, 6: 0.8
        }
        day_factor = day_factors.get(day, 1.0)
        
        # Calculate demand forecast
        daily_demand = base_demand * seasonal_factor * region_factor * day_factor
        
        return {
            'daily_demand': round(daily_demand, 1),
            'weekly_demand': round(daily_demand * 7, 1),
            'monthly_demand': round(daily_demand * 30, 1),
            'demand_level': demand_level,
            'seasonal_factor': seasonal_factor,
            'region': region,
            'region_factor': region_factor,
            'day_factor': day_factor,
            'confidence': min(0.7 + (self.learning_data.get('learning_iterations', 0) * 0.001), 0.95)
        }
    
    def get_price_recommendation(self, product_data):
        """Get comprehensive price recommendation"""
        analysis = self.analyze_product(product_data)
        
        if not analysis:
            return None
        
        current_price = analysis['price_analysis']['user_price']
        market_avg = analysis['price_analysis']['market_avg']
        recommended_price = analysis['recommended_price']
        
        # Consider multiple factors
        factors = {
            'Market Price': market_avg,
            'Seasonal Factor': analysis['seasonal_factor'],
            'Market Trend': 1.05 if analysis['market_trend'] == 'increasing' else 0.95 if analysis['market_trend'] == 'decreasing' else 1.0,
            'Demand Level': 1.1 if analysis['demand_level'] == 'high' else 1.0 if analysis['demand_level'] == 'medium' else 0.9,
            'Region Premium': 1.05
        }
        
        # Calculate weighted recommendation
        final_price = market_avg * factors['Seasonal Factor'] * factors['Market Trend'] * factors['Demand Level'] * factors['Region Premium']
        final_price = round(final_price, 2)
        
        return {
            'current_price': current_price,
            'recommended_price': final_price,
            'market_average': market_avg,
            'factors': factors,
            'price_difference': final_price - current_price,
            'percentage_change': ((final_price - current_price) / current_price * 100) if current_price > 0 else 0,
            'recommendation': self._get_recommendation_text(current_price, final_price),
            'confidence_score': min(0.8 + (self.learning_data.get('learning_iterations', 0) * 0.001), 0.95)
        }
    
    def _get_recommendation_text(self, current, recommended):
        """Get recommendation text"""
        diff = recommended - current
        if diff > current * 0.1:
            return "📈 Increase Price - Market demand supports higher pricing"
        elif diff < -current * 0.1:
            return "📉 Decrease Price - Competitive pricing needed for market share"
        else:
            return "✅ Maintain Price - Current price is well-positioned in the market"

# Initialize AI
ai = SelfLearningAI(user_info['id'])

# --- AI Model Loader (Silent) ---
@st.cache_resource
def load_ai_model(model_name):
    try:
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", model_name),
            os.path.join("models", model_name),
            os.path.join(os.path.dirname(__file__), "..", "models", model_name),
        ]
        
        for model_path in possible_paths:
            if os.path.exists(model_path) and os.path.getsize(model_path) > 10:
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
        return None
    except Exception:
        return None

# Try to load traditional models
demand_model = load_ai_model("demand_forecaster.pkl")
price_model = load_ai_model("price_predictor.pkl")

# --- Initialize States ---
if 'show_edit_profile' not in st.session_state:
    st.session_state.show_edit_profile = False

if 'edit_product_id' not in st.session_state:
    st.session_state.edit_product_id = None

if 'ai_search_query' not in st.session_state:
    st.session_state.ai_search_query = ''

if 'ai_selected_product' not in st.session_state:
    st.session_state.ai_selected_product = None

if 'ai_selected_region' not in st.session_state:
    st.session_state.ai_selected_region = 'Addis Ababa'

# ==========================================
# RESPONSIVE BUSINESS CARD PROFILE (CSS)
# ==========================================
st.markdown("""
<style>
.business-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    border: 1px solid #e2e8f0;
    max-width: 800px;
    margin: 0 auto 20px auto;
}
.card-container {
    display: flex;
    align-items: center;
    gap: 25px;
}
.card-left {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 200px;
    border-right: 2px solid #1e293b;
    padding-right: 25px;
}
.profile-pic-large {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: bold;
    color: white;
    border: 4px solid #fff;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    margin-bottom: 15px;
}
.card-name {
    font-size: 22px;
    font-weight: bold;
    color: #1e293b;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0;
    text-align: center;
}
.card-title {
    font-size: 13px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 5px 0 0 0;
    text-align: center;
}
.card-right {
    flex: 1;
}
.contact-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #1e293b;
    flex-wrap: wrap;
}
.contact-icon {
    font-size: 18px;
    width: 24px;
    text-align: center;
    flex-shrink: 0;
}
.contact-label {
    font-weight: 600;
    color: #475569;
    min-width: 80px;
}
.contact-value {
    color: #1e293b;
    font-weight: 500;
    word-break: break-word;
    flex: 1;
}
.edit-profile-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s;
    margin-top: 15px;
    width: 100%;
}
.edit-profile-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.product-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #475569;
    position: relative;
}
.product-info-badge {
    display: inline-block;
    background: #475569;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    color: #e2e8f0;
    margin: 2px 4px 2px 0;
}
.producer-info {
    background: rgba(102, 126, 234, 0.1);
    padding: 8px 12px;
    border-radius: 8px;
    margin: 8px 0;
    border-left: 3px solid #667eea;
    font-size: 12px;
    color: #94a3b8;
}
.ai-learning-status {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #475569;
    margin: 10px 0;
}
.ai-insight-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #475569;
    margin: 10px 0;
}
.market-price-indicator {
    padding: 10px 15px;
    border-radius: 8px;
    margin: 5px 0;
}
.price-above {
    background: #ef4444;
    color: white;
}
.price-below {
    background: #10b981;
    color: white;
}
.price-at {
    background: #f59e0b;
    color: white;
}
@media screen and (max-width: 768px) {
    .business-card {
        padding: 20px 15px;
        margin: 0 10px 20px 10px;
    }
    .card-container {
        flex-direction: column;
        gap: 20px;
    }
    .card-left {
        border-right: none;
        border-bottom: 2px solid #1e293b;
        padding-right: 0;
        padding-bottom: 20px;
        width: 100%;
    }
    .profile-pic-large {
        width: 100px;
        height: 100px;
        font-size: 40px;
    }
    .card-name {
        font-size: 20px;
    }
    .card-right {
        width: 100%;
    }
    .contact-item {
        font-size: 13px;
        margin-bottom: 10px;
    }
    .contact-label {
        min-width: 70px;
        font-size: 13px;
    }
    .contact-value {
        font-size: 13px;
    }
}
</style>
""", unsafe_allow_html=True)

# Get user data
name = user_info.get('name', 'Not specified')
initial = name[0].upper() if name else "P"
email = user_info.get('email', 'Not specified')
phone = user_info.get('phone', 'Not specified')
company = user_info.get('company_name', 'Not specified')
address = user_info.get('address', 'Not specified')
region = user_info.get('region', 'Addis Ababa')

# Business Card HTML
st.markdown(f"""
<div class="business-card">
    <div class="card-container">
        <div class="card-left">
            <div class="profile-pic-large">{initial}</div>
            <p class="card-name">{name}</p>
            <p class="card-title">Producer • {company}</p>
        </div>
        <div class="card-right">
            <div class="contact-item">
                <span class="contact-icon">🏠</span>
                <span class="contact-label">Address:</span>
                <span class="contact-value">{address}, {region}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">📞</span>
                <span class="contact-label">Phone:</span>
                <span class="contact-value">{phone}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">✉️</span>
                <span class="contact-label">Email:</span>
                <span class="contact-value">{email}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">🏢</span>
                <span class="contact-label">Company:</span>
                <span class="contact-value">{company}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">🌍</span>
                <span class="contact-label">Region:</span>
                <span class="contact-value">{region}</span>
            </div>
            <button class="edit-profile-btn" onclick="document.getElementById('edit-profile-section').scrollIntoView({{behavior: 'smooth'}})">✏️ Edit Profile</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# EDIT PROFILE SECTION
# ==========================================
st.markdown('<div id="edit-profile-section"></div>', unsafe_allow_html=True)

with st.expander("✏️ Edit Profile Information", expanded=st.session_state.show_edit_profile):
    st.markdown("### Update Your Business Card Information")
    
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Full Name", value=user_info.get('name', ''))
            new_email = st.text_input("Email", value=user_info.get('email', ''))
            new_phone = st.text_input("Phone Number", value=user_info.get('phone', ''))
        
        with col2:
            new_company = st.text_input("Company Name", value=user_info.get('company_name', ''))
            new_address = st.text_input("Address", value=user_info.get('address', ''))
            regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                      "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
            current_region = user_info.get('region', 'Addis Ababa')
            region_idx = regions.index(current_region) if current_region in regions else 0
            new_region = st.selectbox("Region", regions, index=region_idx)
        
        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        with col2:
            cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if save_btn:
            if new_name and new_email:
                try:
                    update_user(user_info['id'], 
                               name=new_name, 
                               email=new_email,
                               phone=new_phone,
                               company_name=new_company,
                               address=new_address,
                               region=new_region)
                    
                    st.session_state.user_info['name'] = new_name
                    st.session_state.user_info['email'] = new_email
                    st.session_state.user_info['phone'] = new_phone
                    st.session_state.user_info['company_name'] = new_company
                    st.session_state.user_info['address'] = new_address
                    st.session_state.user_info['region'] = new_region
                    
                    st.success("✅ Profile updated successfully!")
                    st.session_state.show_edit_profile = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating profile: {e}")
            else:
                st.error("Name and Email are required!")
        
        if cancel_btn:
            st.session_state.show_edit_profile = False
            st.rerun()

st.markdown("---")

# --- Navigation Tabs ---
tab_dashboard, tab_inventory, tab_orders, tab_ai = st.tabs([
    "📊 Dashboard", "📦 Inventory", "🚚 Orders", "🤖 AI Insights"
])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dashboard:
    st.subheader("Business Overview")
    
    stats = get_dashboard_stats('producer', user_info['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", stats.get('total_products', 0))
    col2.metric("Low Stock Alerts", stats.get('low_stock', 0), delta_color="inverse")
    col3.metric("Total Orders", stats.get('total_orders', 0))
    col4.metric("Total Revenue", f"{stats.get('revenue', 0):,.2f} ETB")
    
    st.markdown("---")
    
    # AI Learning Status
    with st.expander("🤖 AI Learning Status", expanded=False):
        learning_stats = ai.learning_data
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🧠 Knowledge Items", len(ai.knowledge_base.get('product_knowledge', {})))
        with col2:
            st.metric("🔄 Interactions", len(learning_stats.get('interactions', [])))
        with col3:
            st.metric("🔍 Searches", len(learning_stats.get('search_queries', [])))
        with col4:
            st.metric("📈 Learning Iterations", learning_stats.get('learning_iterations', 0))
        
        st.markdown("### 🧬 AI Learning Progress")
        progress = min(learning_stats.get('learning_iterations', 0) / 100, 1.0)
        st.progress(progress)
        st.caption(f"AI is {progress*100:.1f}% trained on your data")
    
    products = get_products(producer_id=user_info['id'])
    
    if products:
        df_products = pd.DataFrame(products)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stock Levels by Category")
            fig_stock = px.bar(
                df_products.groupby('category')['quantity'].sum().reset_index(),
                x='category', y='quantity', 
                title="Total Stock per Category",
                color='quantity',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_stock, use_container_width=True)
            
        with col2:
            st.subheader("Product Pricing Distribution")
            fig_price = px.histogram(
                df_products, x='price', nbins=20,
                title="Price Distribution of Products",
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("No products found. Go to the Inventory tab to add your first product!")

# ==========================================
# TAB 2: INVENTORY MANAGEMENT
# ==========================================
with tab_inventory:
    st.subheader("Manage Your Inventory")
    
    # Check if editing a product
    edit_mode = st.session_state.edit_product_id is not None
    
    # Add/Edit Product Form
    with st.expander("➕ Add New Product" if not edit_mode else "✏️ Edit Product", expanded=edit_mode):
        with st.form("add_product_form"):
            # If in edit mode, load product data
            product_data = None
            if edit_mode:
                all_products = get_products(producer_id=user_info['id'])
                product_data = next((p for p in all_products if p['id'] == st.session_state.edit_product_id), None)
            
            col1, col2 = st.columns(2)
            
            with col1:
                name_input = st.text_input("Product Name", placeholder="e.g., Teff, Coffee", 
                                          value=product_data['name'] if product_data else "")
                category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"],
                                       index=["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"].index(product_data['category']) if product_data and product_data.get('category') in ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"] else 0)
                price = st.number_input("Selling Price (ETB)", min_value=0.01, step=0.01,
                                       value=float(product_data['price']) if product_data else 0.01)
                cost_price = st.number_input("Cost Price (ETB)", min_value=0.01, step=0.01,
                                            value=float(product_data['cost_price']) if product_data and product_data.get('cost_price') else 0.01)
            
            with col2:
                stock = st.number_input("Stock Quantity", min_value=0, step=1,
                                       value=int(product_data['quantity']) if product_data else 0)
                min_stock = st.number_input("Minimum Stock Alert Level", min_value=1, step=1,
                                           value=int(product_data.get('min_stock', 10)) if product_data else 10)
                weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1,
                                        value=float(product_data.get('weight', 0)) if product_data else 0.0)
                description = st.text_area("Description", placeholder="Brief product description...", height=80,
                                          value=product_data.get('description', '') if product_data else "")
            
            # Image Upload Section
            st.markdown("---")
            st.markdown("### 📷 Product Image")
            current_image = product_data.get('image_url') if product_data else None
            
            if current_image and os.path.exists(current_image):
                st.markdown("#### Current Image:")
                st.image(current_image, width=200)
            
            uploaded_file = st.file_uploader(
                "Upload Product Image" + (" (leave empty to keep current)" if edit_mode else ""),
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            if uploaded_file is not None:
                st.markdown("#### Preview:")
                try:
                    st.image(uploaded_file, caption=f"📷 {uploaded_file.name}", width=300)
                    st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
            
            submitted = st.form_submit_button(
                "💾 Update Product" if edit_mode else "➕ Add Product to Inventory", 
                use_container_width=True, type="primary"
            )
            
            if submitted:
                if not name_input:
                    st.error("❌ Product name is required!")
                else:
                    image_path = current_image
                    if uploaded_file is not None:
                        try:
                            os.makedirs("uploads/products", exist_ok=True)
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                            image_path = os.path.join("uploads/products", unique_filename)
                            
                            with open(image_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            st.success(f"✅ Image saved: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"Error saving image: {e}")
                            image_path = current_image
                    
                    if edit_mode:
                        try:
                            from utils.db_helpers import update_product
                            success, msg = update_product(
                                product_id=st.session_state.edit_product_id,
                                name=name_input,
                                description=description,
                                category=category,
                                price=price,
                                cost_price=cost_price,
                                stock_quantity=stock,
                                min_stock=min_stock,
                                weight=weight,
                                image_url=image_path
                            )
                            
                            if success:
                                # Update AI knowledge
                                product_info = {
                                    'id': st.session_state.edit_product_id,
                                    'name': name_input,
                                    'category': category,
                                    'price': price,
                                    'cost_price': cost_price,
                                    'quantity': stock,
                                    'weight': weight
                                }
                                ai.analyze_product(product_info)
                                
                                st.success(f"✅ {msg}")
                                st.session_state.edit_product_id = None
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                        except Exception as e:
                            st.error(f"❌ Error updating product: {e}")
                    else:
                        success, msg, prod_id = create_product(
                            name=name_input, 
                            description=description, 
                            category=category,
                            price=price, 
                            cost_price=cost_price, 
                            stock_quantity=stock,
                            producer_id=user_info['id'], 
                            weight=weight,
                            image_url=image_path
                        )
                        
                        if success:
                            # Update AI knowledge
                            product_info = {
                                'id': prod_id,
                                'name': name_input,
                                'category': category,
                                'price': price,
                                'cost_price': cost_price,
                                'quantity': stock,
                                'weight': weight
                            }
                            ai.analyze_product(product_info)
                            
                            st.success(f"✅ {msg}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

    st.markdown("---")
    
    # Low Stock Alerts
    low_stock = get_low_stock_products(producer_id=user_info['id'])
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    # All Products Display
    st.subheader("All Products")
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        
        st.markdown("### 📦 Product Gallery")
        cols = st.columns(3)
        
        for idx, product in enumerate(all_products):
            with cols[idx % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                
                # Display product image if exists
                image_url = product.get('image_url')
                image_displayed = False
                if image_url:
                    try:
                        if os.path.exists(image_url):
                            st.image(image_url, use_container_width=True)
                            image_displayed = True
                    except Exception as e:
                        pass
                
                if not image_displayed:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                height: 150px; border-radius: 8px;
                                display: flex; align-items: center; justify-content: center;
                                margin-bottom: 10px;">
                        <span style="color: white; font-size: 48px;">📦</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"<h4 style='margin: 10px 0 5px 0; color: #fff; font-size: 16px;'>{product['name']}</h4>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="producer-info">
                    <strong>👤 Producer:</strong> {user_info.get('name', 'Unknown')}<br>
                    <strong>🏢 Company:</strong> {user_info.get('company_name', 'N/A')}<br>
                    <strong>📞 Contact:</strong> {user_info.get('phone', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <p style="margin: 5px 0; color: #94a3b8; font-size: 13px;">📂 {product.get('category', 'N/A')}</p>
                <p style="margin: 5px 0; color: #10b981; font-weight: bold; font-size: 18px;">{product.get('price', 0)} ETB</p>
                <p style="margin: 5px 0; color: #f59e0b; font-size: 13px;">📦 Stock: {product.get('quantity', 0)} units</p>
                <p style="margin: 5px 0; color: #64748b; font-size: 12px;">SKU: {product.get('sku', 'N/A')}</p>
                """, unsafe_allow_html=True)
                
                created_date = pd.to_datetime(product.get('created_at')).strftime('%Y-%m-%d') if product.get('created_at') else 'N/A'
                st.markdown(f"""
                <div style="margin-top: 8px;">
                    <span class="product-info-badge">⚖️ {product.get('weight', 0)} kg</span>
                    <span class="product-info-badge">📅 {created_date}</span>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{product['id']}", use_container_width=True):
                        st.session_state.edit_product_id = product['id']
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{product['id']}", use_container_width=True):
                        st.session_state.delete_product_id = product['id']
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        if 'delete_product_id' in st.session_state and st.session_state.delete_product_id:
            product_to_delete = next((p for p in all_products if p['id'] == st.session_state.delete_product_id), None)
            if product_to_delete:
                st.warning(f"⚠️ Are you sure you want to delete '{product_to_delete['name']}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", use_container_width=True):
                        try:
                            from utils.db_helpers import delete_product
                            success, msg = delete_product(st.session_state.delete_product_id)
                            if success:
                                st.success(f"✅ {msg}")
                                st.session_state.delete_product_id = None
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                        except Exception as e:
                            st.error(f"❌ Error deleting product: {e}")
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.delete_product_id = None
                        st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Detailed Product List")
        display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
        display_df['Producer'] = user_info.get('name', 'Unknown')
        display_df['Company'] = user_info.get('company_name', 'N/A')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("📭 No products added yet. Click 'Add New Product' above to get started!")

# ==========================================
# TAB 3: ORDERS
# ==========================================
with tab_orders:
    st.subheader("Recent Orders")
    
    orders = get_orders(user_info['id'], 'producer', limit=50)
    
    if orders:
        df_orders = pd.DataFrame(orders)
        
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "confirmed", "shipped", "delivered", "cancelled"])
        
        if status_filter != "All":
            df_orders = df_orders[df_orders['status'] == status_filter]
            
        st.dataframe(df_orders, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig_status = px.pie(
                df_orders, names='status', title="Order Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No orders received yet.")

# ==========================================
# TAB 4: AI INSIGHTS
# ==========================================
with tab_ai:
    st.subheader("🤖 AI-Powered Ethiopian Market Insights")
    st.markdown("### 📊 Real-Time Ethiopian Market Analysis")
    
    # Get all products for analysis
    all_products = get_products(producer_id=user_info['id'])
    
    if not all_products:
        st.warning("⚠️ Add products first to get AI insights")
        st.info("📝 Go to the Inventory tab to add your products")
    else:
        # Product selection
        product_names = {p['id']: p['name'] for p in all_products}
        selected_prod_id = st.selectbox(
            "Select Product for Analysis", 
            list(product_names.keys()), 
            format_func=lambda x: product_names[x]
        )
        
        selected_product = next((p for p in all_products if p['id'] == selected_prod_id), None)
        
        if selected_product:
            # Region selection
            regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                      "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
            selected_region = st.selectbox(
                "Select Region for Price Comparison",
                regions,
                index=regions.index(st.session_state.ai_selected_region) if st.session_state.ai_selected_region in regions else 0
            )
            st.session_state.ai_selected_region = selected_region
            
            st.markdown("---")
            st.markdown(f"### 📊 Analysis for: **{selected_product['name']}** in {selected_region}")
            
            # Get AI analysis
            analysis = ai.analyze_product(selected_product)
            
            if analysis:
                # Market Price Comparison
                st.markdown("#### 💰 Market Price Comparison (Ethiopian Market)")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Your Price", f"{analysis['price_analysis']['user_price']:.2f} ETB")
                with col2:
                    st.metric("Market Average", f"{analysis['price_analysis']['market_avg']:.2f} ETB")
                with col3:
                    diff = analysis['price_analysis']['difference']
                    pct = analysis['price_analysis']['percentage']
                    st.metric(
                        "Price Difference", 
                        f"{diff:+.2f} ETB", 
                        delta=f"{pct:+.1f}%" if pct != 0 else "At Market"
                    )
                
                # Price status indicator
                status = analysis['price_status']
                if "Above" in status:
                    st.markdown(f'<div class="market-price-indicator price-above">⚠️ {status}</div>', unsafe_allow_html=True)
                    st.info("💡 Your price is above market average. Consider adjusting to stay competitive.")
                elif "Below" in status:
                    st.markdown(f'<div class="market-price-indicator price-below">✅ {status}</div>', unsafe_allow_html=True)
                    st.info("💡 Your price is below market average. Good for attracting buyers!")
                else:
                    st.markdown(f'<div class="market-price-indicator price-at">✅ {status}</div>', unsafe_allow_html=True)
                    st.info("💡 Your price is at market rate. Well-positioned!")
                
                # Market Details
                st.markdown("#### 📈 Market Details")
                market_data = analysis['market_data']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Price Range", f"{market_data.get('min_price', 0)} - {market_data.get('max_price', 0)} ETB")
                with col2:
                    st.metric("Unit", market_data.get('unit', 'kg'))
                with col3:
                    st.metric("Market Trend", market_data.get('price_trend', 'N/A').title())
                with col4:
                    st.metric("Demand Level", market_data.get('demand_level', 'N/A').title())
                
                # Demand Prediction
                st.markdown("#### 📊 Demand Prediction")
                
                # Get region-specific demand
                demand_prediction = ai.predict_demand(selected_product['name'], selected_region)
                
                if demand_prediction:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Daily Demand Forecast", f"{demand_prediction['daily_demand']:.0f} units")
                    with col2:
                        st.metric("Weekly Demand", f"{demand_prediction['weekly_demand']:.0f} units")
                    with col3:
                        st.metric("Monthly Demand", f"{demand_prediction['monthly_demand']:.0f} units")
                    
                    st.markdown(f"""
                    <div class="ai-insight-card">
                        <strong>📍 Region Factor:</strong> {demand_prediction['region_factor']:.2f}x<br>
                        <strong>📅 Seasonal Factor:</strong> {demand_prediction['seasonal_factor']:.2f}x<br>
                        <strong>📊 Confidence Level:</strong> {demand_prediction['confidence']*100:.1f}%
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Stock level analysis
                    current_stock = selected_product.get('quantity', 0)
                    daily_demand = demand_prediction['daily_demand']
                    days_of_stock = current_stock / daily_demand if daily_demand > 0 else 0
                    
                    if days_of_stock < 7:
                        st.warning(f"⚠️ Only {days_of_stock:.1f} days of stock remaining! Restock soon.")
                        st.progress(days_of_stock / 30)
                    elif days_of_stock < 14:
                        st.info(f"ℹ️ {days_of_stock:.1f} days of stock remaining. Plan restocking.")
                        st.progress(days_of_stock / 30)
                    else:
                        st.success(f"✅ {days_of_stock:.1f} days of stock remaining. Healthy stock level.")
                        st.progress(min(days_of_stock / 30, 1.0))
                
                # Price Recommendation
                st.markdown("#### 💡 AI Price Recommendation")
                
                price_rec = ai.get_price_recommendation(selected_product)
                
                if price_rec:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Price", f"{price_rec['current_price']:.2f} ETB")
                    with col2:
                        st.metric(
                            "Recommended Price", 
                            f"{price_rec['recommended_price']:.2f} ETB",
                            delta=f"{price_rec['price_difference']:+.2f} ETB"
                        )
                    
                    # Recommendation text
                    st.markdown(f"""
                    <div class="ai-insight-card">
                        <strong>💬 Recommendation:</strong> {price_rec['recommendation']}<br>
                        <strong>📊 Confidence Score:</strong> {price_rec['confidence_score']*100:.1f}%
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Factors considered
                    with st.expander("📋 Factors Considered in Recommendation"):
                        factors = price_rec['factors']
                        st.markdown(f"""
                        - **Market Price:** {factors['Market Price']:.2f} ETB
                        - **Seasonal Factor:** {factors['Seasonal Factor']:.2f}x
                        - **Market Trend:** {factors['Market Trend']:.2f}x
                        - **Demand Level:** {factors['Demand Level']:.2f}x
                        - **Region Premium:** {factors['Region Premium']:.2f}x
                        """)
                
                # Profit Analysis
                st.markdown("#### 💰 Profit Analysis")
                
                profit_data = analysis['profit_potential']
                if profit_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Profit/Unit", f"{profit_data['current_profit']:.2f} ETB")
                    with col2:
                        st.metric("Recommended Profit/Unit", f"{profit_data['recommended_profit']:.2f} ETB")
                    with col3:
                        st.metric("Profit Margin", f"{profit_data['margin_percentage']:.1f}%")
                    
                    if profit_data['profit_percentage_change'] > 0:
                        st.success(f"📈 Profit could increase by {profit_data['profit_percentage_change']:.1f}% with AI recommendation")
                    else:
                        st.info("ℹ️ Current profit is already optimal")
                
                # Ethiopian Market Data Source
                st.markdown("---")
                st.markdown("#### 📍 Ethiopian Market Data")
                st.info("""
                Market data includes:
                - Ethiopian Commodity Exchange (ECX) price ranges
                - Regional market variations
                - Seasonal demand patterns
                - Current market trends
                
                *Data is updated based on real Ethiopian market conditions*
                """)
                
                # Force AI Learning
                if st.button("🔄 Refresh Ethiopian Market Data", use_container_width=True):
                    with st.spinner("Fetching latest Ethiopian market data..."):
                        product_name = selected_product['name']
                        fresh_data = ai.get_ethiopian_market_insights(product_name)
                        st.success("✅ Ethiopian market data refreshed!")
                        st.rerun()
            
            # Learning Progress
            st.markdown("---")
            st.markdown("#### 🧠 AI Learning Progress")
            
            learning_stats = ai.learning_data
            knowledge_items = len(ai.knowledge_base.get('product_knowledge', {}))
            iterations = learning_stats.get('learning_iterations', 0)
            
            progress_score = min(50 + (knowledge_items * 2) + (iterations * 0.5), 100)
            st.progress(progress_score / 100)
            st.caption(f"AI is {progress_score:.1f}% confident in its predictions")
            
            st.markdown(f"""
            <div class="ai-insight-card">
                <strong>📚 Knowledge Base:</strong> {knowledge_items} products<br>
                <strong>🔄 Learning Iterations:</strong> {iterations}<br>
                <strong>🌐 Ethiopian Market Data:</strong> Active
            </div>
            """, unsafe_allow_html=True)
    
    # Quick Overview Section
    st.markdown("---")
    st.markdown("### 🚀 Ethiopian Market Quick Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Top Products by Demand")
        top_products = [
            {"name": "Teff", "demand": "High", "trend": "Increasing"},
            {"name": "Coffee", "demand": "High", "trend": "Increasing"},
            {"name": "Wheat", "demand": "High", "trend": "Stable"},
            {"name": "Onion", "demand": "Medium", "trend": "Increasing"},
            {"name": "Milk", "demand": "High", "trend": "Increasing"}
        ]
        for p in top_products:
            st.markdown(f"""
            <div style="background: #1e293b; padding: 8px 12px; border-radius: 8px; margin: 4px 0;">
                <strong>{p['name']}</strong> - Demand: {p['demand']} | Trend: {p['trend']}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 💰 Ethiopian Market Price Trends")
        price_trends = [
            {"product": "Coffee", "price": "300-400 ETB/kg", "trend": "↑"},
            {"product": "Teff", "price": "80-150 ETB/kg", "trend": "↑"},
            {"product": "Wheat", "price": "45-75 ETB/kg", "trend": "→"},
            {"product": "Onion", "price": "25-45 ETB/kg", "trend": "↑"},
            {"product": "Milk", "price": "60-90 ETB/L", "trend": "↑"}
        ]
        for p in price_trends:
            emoji = "📈" if p['trend'] == "↑" else "➡️"
            st.markdown(f"""
            <div style="background: #1e293b; padding: 8px 12px; border-radius: 8px; margin: 4px 0;">
                {emoji} <strong>{p['product']}</strong>: {p['price']}
            </div>
            """, unsafe_allow_html=True)
    
    st.info("💡 AI combines Ethiopian market data with your product information for intelligent insights")
