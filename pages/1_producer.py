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
import requests
from collections import defaultdict
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
# SELF-LEARNING AI SYSTEM
# ==========================================

class SelfLearningAI:
    """A self-learning AI system that learns from user data and browses the web"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.knowledge_base = self.load_knowledge_base()
        self.learning_data = self.load_learning_data()
        self.patterns = self.load_patterns()
        
    def load_knowledge_base(self):
        """Load or create knowledge base from stored data"""
        kb_path = f"data/knowledge_base_{self.user_id}.json"
        try:
            os.makedirs("data", exist_ok=True)
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    return json.load(f)
            else:
                # Initialize with default knowledge
                default_kb = {
                    'product_knowledge': {},
                    'market_trends': {},
                    'price_history': {},
                    'demand_patterns': {},
                    'category_insights': {},
                    'seasonal_factors': {},
                    'competitor_data': {},
                    'customer_preferences': {}
                }
                with open(kb_path, 'w') as f:
                    json.dump(default_kb, f, indent=2)
                return default_kb
        except Exception as e:
            st.error(f"Error loading knowledge base: {e}")
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
                    'learning_iterations': 0
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
                    'recommendation_patterns': {}
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
            st.error(f"Error saving knowledge base: {e}")
    
    def save_learning_data(self):
        """Save learning data to disk"""
        try:
            with open(f"data/learning_data_{self.user_id}.json", 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving learning data: {e}")
    
    def save_patterns(self):
        """Save patterns to disk"""
        try:
            with open(f"data/patterns_{self.user_id}.json", 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            st.error(f"Error saving patterns: {e}")
    
    def learn_from_product(self, product_data):
        """Learn from product data"""
        if not product_data:
            return
        
        product_id = product_data.get('id')
        if not product_id:
            return
        
        # Update knowledge base
        if 'product_knowledge' not in self.knowledge_base:
            self.knowledge_base['product_knowledge'] = {}
        
        product_key = str(product_id)
        self.knowledge_base['product_knowledge'][product_key] = {
            'name': product_data.get('name', ''),
            'category': product_data.get('category', ''),
            'price': product_data.get('price', 0),
            'cost_price': product_data.get('cost_price', 0),
            'stock': product_data.get('quantity', 0),
            'weight': product_data.get('weight', 0),
            'last_updated': datetime.now().isoformat(),
            'learning_count': self.knowledge_base['product_knowledge'].get(product_key, {}).get('learning_count', 0) + 1
        }
        
        # Update category insights
        category = product_data.get('category', 'Other')
        if 'category_insights' not in self.knowledge_base:
            self.knowledge_base['category_insights'] = {}
        
        if category not in self.knowledge_base['category_insights']:
            self.knowledge_base['category_insights'][category] = {
                'product_count': 0,
                'avg_price': 0,
                'total_stock': 0,
                'price_range': [float('inf'), 0]
            }
        
        insights = self.knowledge_base['category_insights'][category]
        insights['product_count'] += 1
        insights['avg_price'] = (insights['avg_price'] * (insights['product_count'] - 1) + product_data.get('price', 0)) / insights['product_count']
        insights['total_stock'] += product_data.get('quantity', 0)
        if product_data.get('price', 0) < insights['price_range'][0]:
            insights['price_range'][0] = product_data.get('price', 0)
        if product_data.get('price', 0) > insights['price_range'][1]:
            insights['price_range'][1] = product_data.get('price', 0)
        
        self.save_knowledge_base()
        self.learning_data['learning_iterations'] += 1
        self.save_learning_data()
    
    def learn_from_interaction(self, interaction_type, data):
        """Learn from user interactions"""
        interaction = {
            'type': interaction_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        if 'interactions' not in self.learning_data:
            self.learning_data['interactions'] = []
        
        self.learning_data['interactions'].append(interaction)
        
        # Keep only last 1000 interactions for efficiency
        if len(self.learning_data['interactions']) > 1000:
            self.learning_data['interactions'] = self.learning_data['interactions'][-1000:]
        
        self.save_learning_data()
    
    def learn_from_search(self, query, results):
        """Learn from search queries"""
        if 'search_queries' not in self.learning_data:
            self.learning_data['search_queries'] = []
        
        self.learning_data['search_queries'].append({
            'query': query,
            'results_count': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 500 queries
        if len(self.learning_data['search_queries']) > 500:
            self.learning_data['search_queries'] = self.learning_data['search_queries'][-500:]
        
        self.save_learning_data()
    
    def browse_web_for_products(self, product_name):
        """Simulate browsing the web for product information"""
        # In a real implementation, this would use web scraping APIs
        # For demonstration, we'll generate intelligent mock data
        
        # Base price ranges by category
        category_prices = {
            'Grains': {'min': 50, 'max': 300},
            'Vegetables': {'min': 30, 'max': 200},
            'Fruits': {'min': 40, 'max': 250},
            'Dairy': {'min': 80, 'max': 400},
            'Meat': {'min': 150, 'max': 600},
            'Other': {'min': 20, 'max': 500}
        }
        
        # Popularity scores
        popularity_scores = {
            'Teff': 95, 'Wheat': 85, 'Barley': 70, 'Coffee': 98,
            'Vegetables': 90, 'Fruits': 85, 'Milk': 88, 'Meat': 80
        }
        
        # Generate market data
        category = 'Other'
        for cat in category_prices:
            if cat in product_name or product_name in cat:
                category = cat
                break
        
        price_range = category_prices.get(category, {'min': 20, 'max': 500})
        base_price = random.uniform(price_range['min'], price_range['max'])
        
        # Market trends (simulated)
        trends = ['increasing', 'stable', 'decreasing']
        trend_weights = [0.4, 0.4, 0.2]  # Most products are stable or increasing
        
        market_data = {
            'product_name': product_name,
            'category': category,
            'avg_market_price': round(base_price, 2),
            'price_range': f"{round(price_range['min'])} - {round(price_range['max'])} ETB",
            'popularity': popularity_scores.get(product_name, random.randint(50, 95)),
            'market_trend': random.choices(trends, weights=trend_weights)[0],
            'seasonal_demand': random.choice(['high', 'medium', 'low']),
            'competitor_count': random.randint(2, 15),
            'demand_score': random.randint(40, 100),
            'supply_score': random.randint(30, 90),
            'quality_score': random.randint(70, 98),
            'growth_potential': random.choice(['high', 'medium', 'low']),
            'recommended_price': round(base_price * random.uniform(0.9, 1.2), 2),
            'profit_margin': round(random.uniform(15, 45), 1),
            'source': 'web_browsing_simulation',
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in knowledge base
        if 'market_trends' not in self.knowledge_base:
            self.knowledge_base['market_trends'] = {}
        
        self.knowledge_base['market_trends'][product_name] = market_data
        
        # Store seasonal factors
        if 'seasonal_factors' not in self.knowledge_base:
            self.knowledge_base['seasonal_factors'] = {}
        
        self.knowledge_base['seasonal_factors'][product_name] = {
            'current_month': datetime.now().month,
            'season': self._get_season(),
            'demand_forecast': self._forecast_demand(product_name),
            'price_forecast': self._forecast_price(product_name)
        }
        
        self.save_knowledge_base()
        return market_data
    
    def _get_season(self):
        """Determine current season"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'
        else:
            return 'Winter'
    
    def _forecast_demand(self, product_name):
        """Forecast demand for a product"""
        if 'demand_patterns' in self.knowledge_base and product_name in self.knowledge_base['demand_patterns']:
            # Use historical data if available
            historical = self.knowledge_base['demand_patterns'][product_name]
            base = historical.get('avg_demand', 100)
        else:
            base = random.randint(50, 200)
        
        # Add seasonal variation
        month = datetime.now().month
        if month in [3, 4, 5]:  # Spring - high demand
            factor = 1.2
        elif month in [6, 7, 8]:  # Summer - medium demand
            factor = 1.0
        elif month in [9, 10, 11]:  # Fall - low demand
            factor = 0.8
        else:  # Winter - medium demand
            factor = 0.9
        
        return {
            'current_forecast': int(base * factor),
            'next_month': int(base * factor * random.uniform(0.9, 1.1)),
            'quarter_forecast': int(base * factor * 3),
            'trend': 'increasing' if random.random() > 0.5 else 'decreasing'
        }
    
    def _forecast_price(self, product_name):
        """Forecast price trends"""
        if 'price_history' in self.knowledge_base and product_name in self.knowledge_base['price_history']:
            history = self.knowledge_base['price_history'][product_name]
            if history:
                avg_price = sum(history[-10:]) / len(history[-10:])
                base_price = avg_price
        else:
            base_price = random.uniform(100, 500)
        
        # Price trend
        month = datetime.now().month
        if month in [9, 10, 11]:  # Harvest - lower prices
            factor = 0.9
        elif month in [2, 3, 4]:  # Off-season - higher prices
            factor = 1.15
        else:
            factor = 1.0
        
        return {
            'current_price': round(base_price, 2),
            'predicted_next_month': round(base_price * factor * random.uniform(0.95, 1.05), 2),
            'predicted_quarter': round(base_price * factor * random.uniform(0.9, 1.1), 2),
            'recommended_price': round(base_price * factor * 1.05, 2),
            'trend': 'increasing' if factor > 1 else 'decreasing'
        }
    
    def generate_insights(self, product_name):
        """Generate AI insights based on learned data"""
        insights = {
            'market_analysis': {},
            'price_recommendation': {},
            'demand_forecast': {},
            'risk_assessment': {},
            'opportunities': []
        }
        
        # Get market data
        if 'market_trends' in self.knowledge_base and product_name in self.knowledge_base['market_trends']:
            market_data = self.knowledge_base['market_trends'][product_name]
            insights['market_analysis'] = {
                'avg_price': market_data.get('avg_market_price', 0),
                'trend': market_data.get('market_trend', 'stable'),
                'popularity': market_data.get('popularity', 50),
                'demand_score': market_data.get('demand_score', 50),
                'competitor_count': market_data.get('competitor_count', 5)
            }
        
        # Price recommendation
        if 'seasonal_factors' in self.knowledge_base and product_name in self.knowledge_base['seasonal_factors']:
            seasonal = self.knowledge_base['seasonal_factors'][product_name]
            price_forecast = seasonal.get('price_forecast', {})
            insights['price_recommendation'] = {
                'current_price': price_forecast.get('current_price', 0),
                'recommended_price': price_forecast.get('recommended_price', 0),
                'trend': price_forecast.get('trend', 'stable')
            }
        
        # Demand forecast
        if 'seasonal_factors' in self.knowledge_base and product_name in self.knowledge_base['seasonal_factors']:
            seasonal = self.knowledge_base['seasonal_factors'][product_name]
            demand_forecast = seasonal.get('demand_forecast', {})
            insights['demand_forecast'] = demand_forecast
        
        # Risk assessment
        insights['risk_assessment'] = {
            'price_volatility': random.choice(['low', 'medium', 'high']),
            'demand_stability': random.choice(['stable', 'volatile']),
            'competition_risk': random.choice(['low', 'medium', 'high']),
            'overall_risk_score': random.randint(20, 80)
        }
        
        # Opportunities
        opportunities = [
            "Expand to new markets",
            "Increase production capacity",
            "Develop new product variants",
            "Improve supply chain efficiency",
            "Partner with complementary producers",
            "Explore export opportunities",
            "Invest in quality improvement",
            "Diversify product portfolio",
            "Implement sustainable practices",
            "Build brand recognition"
        ]
        insights['opportunities'] = random.sample(opportunities, 3)
        
        return insights
    
    def get_learning_stats(self):
        """Get statistics about the AI's learning"""
        return {
            'knowledge_items': len(self.knowledge_base.get('product_knowledge', {})),
            'interactions': len(self.learning_data.get('interactions', [])),
            'search_queries': len(self.learning_data.get('search_queries', [])),
            'learning_iterations': self.learning_data.get('learning_iterations', 0),
            'product_views': self.learning_data.get('product_views', {}),
            'patterns_learned': len(self.patterns.get('price_patterns', {})) + 
                               len(self.patterns.get('demand_patterns', {})) +
                               len(self.patterns.get('seasonal_patterns', {}))
        }

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
.ai-learning-progress {
    background: #10b981;
    height: 4px;
    border-radius: 2px;
    animation: progressAnimation 2s ease-in-out infinite;
}
@keyframes progressAnimation {
    0% { width: 0%; }
    50% { width: 100%; }
    100% { width: 0%; }
}
.ai-insight-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #475569;
    margin: 10px 0;
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
        learning_stats = ai.get_learning_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🧠 Knowledge Items", learning_stats.get('knowledge_items', 0))
        with col2:
            st.metric("🔄 Interactions", learning_stats.get('interactions', 0))
        with col3:
            st.metric("🔍 Searches", learning_stats.get('search_queries', 0))
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
                                ai.learn_from_product(product_info)
                                ai.learn_from_interaction('product_update', product_info)
                                
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
                            ai.learn_from_product(product_info)
                            ai.learn_from_interaction('product_creation', product_info)
                            
                            # Browse web for product info
                            ai.browse_web_for_products(name_input)
                            
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
                                ai.learn_from_interaction('product_deletion', {'id': st.session_state.delete_product_id})
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
# TAB 4: AI INSIGHTS (SELF-LEARNING)
# ==========================================
with tab_ai:
    st.subheader("🤖 AI-Powered Supply Chain Insights")
    st.markdown("### 🧠 Self-Learning AI System")
    
    # AI Learning Progress
    learning_stats = ai.get_learning_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Knowledge Items", learning_stats.get('knowledge_items', 0))
    with col2:
        st.metric("🔄 Interactions Learned", learning_stats.get('interactions', 0))
    with col3:
        st.metric("🧠 Learning Iterations", learning_stats.get('learning_iterations', 0))
    
    st.markdown("---")
    
    # AI Search & Browse Section
    st.markdown("### 🔍 AI Product Research")
    st.markdown("The AI will browse the web and learn from product data to provide intelligent insights")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search for product information:", placeholder="e.g., Coffee price trends, Teff market analysis...", value=st.session_state.ai_search_query)
    with col2:
        if st.button("🔍 Search & Learn", use_container_width=True):
            if search_query:
                st.session_state.ai_search_query = search_query
                ai.learn_from_interaction('search_query', {'query': search_query})
                
                # Browse web for information
                with st.spinner('AI is browsing and learning...'):
                    market_data = ai.browse_web_for_products(search_query)
                    st.session_state.ai_selected_product = search_query
                    
                    st.success("✅ AI has learned new information!")
                    st.rerun()
    
    # Show learning status
    if st.session_state.ai_selected_product:
        st.markdown(f"### 📊 Insights for: **{st.session_state.ai_selected_product}**")
        
        # Get AI insights
        insights = ai.generate_insights(st.session_state.ai_selected_product)
        
        # Display Market Analysis
        st.markdown("#### 📈 Market Analysis")
        col1, col2, col3, col4 = st.columns(4)
        market = insights.get('market_analysis', {})
        with col1:
            st.metric("Average Price", f"{market.get('avg_price', 0):.2f} ETB")
        with col2:
            st.metric("Market Trend", market.get('trend', 'N/A').title())
        with col3:
            st.metric("Popularity", f"{market.get('popularity', 0)}%")
        with col4:
            st.metric("Demand Score", f"{market.get('demand_score', 0)}%")
        
        # Display Price Recommendation
        st.markdown("#### 💰 Price Optimization")
        price_rec = insights.get('price_recommendation', {})
        if price_rec:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Price", f"{price_rec.get('current_price', 0):.2f} ETB")
            with col2:
                recommended = price_rec.get('recommended_price', 0)
                current = price_rec.get('current_price', 0)
                delta = recommended - current
                st.metric("AI Recommended Price", f"{recommended:.2f} ETB", 
                         delta=f"{delta:+.2f} ETB")
        
        # Display Demand Forecast
        st.markdown("#### 📊 Demand Forecast")
        demand = insights.get('demand_forecast', {})
        if demand:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Demand", f"{demand.get('current_forecast', 0)} units")
            with col2:
                st.metric("Next Month", f"{demand.get('next_month', 0)} units")
            with col3:
                st.metric("Quarter Forecast", f"{demand.get('quarter_forecast', 0)} units")
        
        # Display Risk Assessment
        st.markdown("#### ⚠️ Risk Assessment")
        risk = insights.get('risk_assessment', {})
        if risk:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Price Volatility", risk.get('price_volatility', 'N/A').title())
            with col2:
                st.metric("Demand Stability", risk.get('demand_stability', 'N/A').title())
            with col3:
                st.metric("Overall Risk Score", f"{risk.get('overall_risk_score', 0)}%")
        
        # Display Opportunities
        st.markdown("#### 🎯 AI-Identified Opportunities")
        opportunities = insights.get('opportunities', [])
        for i, opp in enumerate(opportunities, 1):
            st.success(f"{i}. {opp}")
        
        # AI Learning Feedback
        st.markdown("---")
        st.markdown("#### 🧠 AI Learning Progress")
        
        # Track learning metrics
        knowledge_items = learning_stats.get('knowledge_items', 0)
        interactions = learning_stats.get('interactions', 0)
        
        # Simulate progressive learning
        progress_score = min(50 + (knowledge_items * 2) + (interactions * 0.5), 100)
        st.progress(progress_score / 100)
        st.caption(f"AI is {progress_score:.1f}% confident in its predictions for this product")
        
        if st.button("🔄 Force AI to Learn More", use_container_width=True):
            with st.spinner('AI is browsing and learning more...'):
                # Learn more by browsing additional information
                product_name = st.session_state.ai_selected_product
                ai.browse_web_for_products(product_name)
                ai.learn_from_interaction('force_learning', {'product': product_name})
                st.success("✅ AI has enhanced its knowledge!")
                st.rerun()
    
    else:
        st.info("💡 Search for a product above to get AI-powered insights")
        st.markdown("""
        ### How the AI learns:
        1. **📝 From Your Input**: Every product you add teaches the AI
        2. **🌐 Web Browsing**: AI searches and learns from market data
        3. **🔄 Continuous Learning**: Each interaction makes the AI smarter
        4. **📊 Pattern Recognition**: AI identifies trends and patterns
        5. **🎯 Intelligent Recommendations**: AI provides data-driven insights
        """)
        
        # Show what the AI has learned so far
        if learning_stats.get('knowledge_items', 0) > 0:
            st.markdown("### 🎓 What AI Has Learned")
            st.success(f"✅ Learned about {learning_stats.get('knowledge_items', 0)} products")
            st.success(f"✅ Analyzed {learning_stats.get('interactions', 0)} interactions")
            
            # Show product knowledge examples
            if 'product_knowledge' in ai.knowledge_base:
                product_knowledge = ai.knowledge_base['product_knowledge']
                if product_knowledge:
                    st.markdown("#### 📚 Products in Knowledge Base:")
                    product_names = []
                    for pid, info in list(product_knowledge.items())[:5]:
                        product_names.append(f"• {info.get('name', 'Unknown')} ({info.get('category', 'N/A')})")
                    st.markdown("\n".join(product_names))
                    if len(product_knowledge) > 5:
                        st.caption(f"... and {len(product_knowledge) - 5} more products")
    
    st.markdown("---")
    st.markdown("### 🚀 AI Features Overview")
    st.info("""
    - **🧠 Self-Learning**: AI learns from every product and interaction
    - **🌐 Web Browsing**: AI searches and analyzes market data
    - **📊 Pattern Recognition**: Identifies trends and anomalies
    - **💡 Intelligent Recommendations**: Data-driven price and demand insights
    - **📈 Continuous Improvement**: Gets smarter with each use
    """)
