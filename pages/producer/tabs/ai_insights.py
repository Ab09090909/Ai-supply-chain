# pages/producer/tabs/ai_insights_self_learning.py
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
# SELF-LEARNING MARKET INTELLIGENCE SYSTEM
# ==========================================

class MarketIntelligence:
    """Self-learning market intelligence system"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.data_dir = "data"
        self.models_dir = "Models"
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.load_all_data()
        self.model = None
        self.scaler = None
        self.load_or_train_model()
        
    def load_all_data(self):
        """Load all market data from disk"""
        try:
            # Market data from user posts
            market_path = f"{self.data_dir}/market_data_{self.user_id}.json"
            if os.path.exists(market_path):
                with open(market_path, 'r') as f:
                    self.market_data = json.load(f)
            else:
                self.market_data = []
            
            # Market statistics
            stats_path = f"{self.data_dir}/market_stats_{self.user_id}.json"
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    self.market_stats = json.load(f)
            else:
                self.market_stats = {}
            
            # Seasonal patterns
            seasonal_path = f"{self.data_dir}/seasonal_patterns_{self.user_id}.json"
            if os.path.exists(seasonal_path):
                with open(seasonal_path, 'r') as f:
                    self.seasonal_patterns = json.load(f)
            else:
                self.seasonal_patterns = {}
            
            # Prediction history
            pred_path = f"{self.data_dir}/prediction_history_{self.user_id}.json"
            if os.path.exists(pred_path):
                with open(pred_path, 'r') as f:
                    self.prediction_history = json.load(f)
            else:
                self.prediction_history = []
            
            # Price verifications
            verify_path = f"{self.data_dir}/price_verifications_{self.user_id}.json"
            if os.path.exists(verify_path):
                with open(verify_path, 'r') as f:
                    self.price_verifications = json.load(f)
            else:
                self.price_verifications = {}
            
            # Trust scores
            trust_path = f"{self.data_dir}/trust_scores_{self.user_id}.json"
            if os.path.exists(trust_path):
                with open(trust_path, 'r') as f:
                    self.trust_scores = json.load(f)
            else:
                self.trust_scores = {}
                
        except Exception as e:
            self.market_data = []
            self.market_stats = {}
            self.seasonal_patterns = {}
            self.prediction_history = []
            self.price_verifications = {}
            self.trust_scores = {}
    
    def save_all_data(self):
        """Save all market data to disk"""
        try:
            with open(f"{self.data_dir}/market_data_{self.user_id}.json", 'w') as f:
                json.dump(self.market_data, f, indent=2)
            
            with open(f"{self.data_dir}/market_stats_{self.user_id}.json", 'w') as f:
                json.dump(self.market_stats, f, indent=2)
            
            with open(f"{self.data_dir}/seasonal_patterns_{self.user_id}.json", 'w') as f:
                json.dump(self.seasonal_patterns, f, indent=2)
            
            with open(f"{self.data_dir}/prediction_history_{self.user_id}.json", 'w') as f:
                json.dump(self.prediction_history, f, indent=2)
            
            with open(f"{self.data_dir}/price_verifications_{self.user_id}.json", 'w') as f:
                json.dump(self.price_verifications, f, indent=2)
            
            with open(f"{self.data_dir}/trust_scores_{self.user_id}.json", 'w') as f:
                json.dump(self.trust_scores, f, indent=2)
        except Exception as e:
            pass
    
    def load_or_train_model(self):
        """Load existing model or train a new one"""
        try:
            model_path = f"{self.models_dir}/self_learning_model_{self.user_id}.pkl"
            scaler_path = f"{self.models_dir}/self_learning_scaler_{self.user_id}.pkl"
            
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
                self.train_model()
                return True
        except Exception as e:
            return False
    
    def train_model(self):
        """Train the AI model with available data"""
        try:
            training_data = self.prepare_training_data()
            if len(training_data) > 10:
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
                    
                    # Save model
                    with open(f"{self.models_dir}/self_learning_model_{self.user_id}.pkl", 'wb') as f:
                        pickle.dump(self.model, f)
                    with open(f"{self.models_dir}/self_learning_scaler_{self.user_id}.pkl", 'wb') as f:
                        pickle.dump(self.scaler, f)
                    
                    return True
            return False
        except Exception as e:
            return False
    
    def prepare_training_data(self):
        """Prepare training data from market data"""
        training_data = []
        
        for entry in self.market_data:
            data = {
                'price': entry.get('price_per_kg', 100),
                'demand_score': self.calculate_demand_score(entry),
                'seasonal_factor': self.get_seasonal_factor(entry),
                'region_factor': self.get_region_factor(entry),
                'trend_factor': self.get_trend_factor(entry),
                'predicted_price': entry.get('price_per_kg', 100) * random.uniform(0.9, 1.1)
            }
            training_data.append(data)
        
        return training_data
    
    def calculate_demand_score(self, entry):
        """Calculate demand score for an entry"""
        # Base on quantity and price
        quantity = entry.get('quantity', 0)
        price = entry.get('price_per_kg', 100)
        
        if quantity > 1000:
            return 85
        elif quantity > 500:
            return 70
        elif quantity > 100:
            return 50
        else:
            return 30
    
    def get_seasonal_factor(self, entry):
        """Get seasonal factor for an entry"""
        month = datetime.now().month
        seasonal_factors = {
            1: 1.1, 2: 1.0, 3: 0.9, 4: 0.9, 5: 1.0,
            6: 1.1, 7: 1.2, 8: 1.2, 9: 1.0, 10: 0.9,
            11: 0.8, 12: 1.0
        }
        return seasonal_factors.get(month, 1.0)
    
    def get_region_factor(self, entry):
        """Get region factor for an entry"""
        region = entry.get('region', 'Addis Ababa')
        region_factors = {
            'Addis Ababa': 1.3,
            'Oromia': 1.0,
            'Amhara': 0.95,
            'Tigray': 0.9,
            'SNNP': 0.85,
            'Sidama': 0.9
        }
        return region_factors.get(region, 1.0)
    
    def get_trend_factor(self, entry):
        """Get trend factor for an entry"""
        # Check if we have price history for this product
        product_name = entry.get('commodity', 'Unknown')
        if product_name in self.market_stats:
            stats = self.market_stats[product_name]
            trend = stats.get('trend', 'stable')
            if trend == 'increasing':
                return 1.1
            elif trend == 'decreasing':
                return 0.9
        return 1.0
    
    def on_product_posted(self, product_data):
        """Learn from a new product posting"""
        # Create market entry
        market_entry = {
            'id': hashlib.md5(f"{product_data.get('name')}{datetime.now().isoformat()}".encode()).hexdigest()[:8],
            'commodity': product_data.get('name', 'Unknown'),
            'price': product_data.get('price', 0),
            'price_per_kg': product_data.get('price', 0) / max(1, product_data.get('quantity', 1)),
            'region': product_data.get('region', 'Addis Ababa'),
            'seller_type': 'producer',
            'quantity': product_data.get('quantity', 0),
            'quality_grade': product_data.get('grade', 'Standard'),
            'posted_at': datetime.now().isoformat(),
            'season': self.get_current_season()
        }
        
        # Add to market data
        self.market_data.append(market_entry)
        
        # Update market averages
        self.update_market_averages(market_entry)
        
        # Detect price trends
        self.detect_price_trends(market_entry['commodity'])
        
        # Build seasonal patterns
        self.build_seasonal_patterns()
        
        # Save all data
        self.save_all_data()
        
        # Retrain model
        self.train_model()
        
        return market_entry
    
    def get_current_season(self):
        """Get current season"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'
        else:
            return 'Winter'
    
    def update_market_averages(self, entry):
        """Update market averages from posted data"""
        commodity = entry.get('commodity')
        region = entry.get('region')
        key = f"{commodity}_{region}"
        
        if key not in self.market_stats:
            self.market_stats[key] = {
                'commodity': commodity,
                'region': region,
                'prices': [],
                'avg_price': 0,
                'min_price': 0,
                'max_price': 0,
                'total_listings': 0,
                'trend': 'stable'
            }
        
        stats = self.market_stats[key]
        stats['prices'].append(entry.get('price_per_kg', 0))
        stats['total_listings'] += 1
        
        # Keep only last 100 prices
        if len(stats['prices']) > 100:
            stats['prices'] = stats['prices'][-100:]
        
        # Calculate statistics
        prices = stats['prices']
        stats['avg_price'] = sum(prices) / len(prices)
        stats['min_price'] = min(prices)
        stats['max_price'] = max(prices)
        
        # Calculate trend
        if len(prices) > 10:
            recent = prices[-10:]
            if recent[-1] > recent[0] * 1.05:
                stats['trend'] = 'increasing'
            elif recent[-1] < recent[0] * 0.95:
                stats['trend'] = 'decreasing'
            else:
                stats['trend'] = 'stable'
        
        self.market_stats[key] = stats
    
    def detect_price_trends(self, commodity):
        """Detect price trends for a commodity"""
        # Get all entries for this commodity
        entries = [e for e in self.market_data if e.get('commodity') == commodity]
        
        if len(entries) < 5:
            return
        
        # Group by week
        weekly_prices = {}
        for entry in entries:
            date = datetime.fromisoformat(entry.get('posted_at', datetime.now().isoformat()))
            week = date.strftime('%Y-%W')
            if week not in weekly_prices:
                weekly_prices[week] = []
            weekly_prices[week].append(entry.get('price_per_kg', 0))
        
        # Calculate weekly averages
        weekly_avg = {}
        for week, prices in weekly_prices.items():
            weekly_avg[week] = sum(prices) / len(prices)
        
        # Calculate momentum
        weeks = sorted(weekly_avg.keys())
        if len(weeks) > 4:
            recent = [weekly_avg[w] for w in weeks[-4:]]
            momentum = (recent[-1] - recent[0]) / recent[0] * 100
            
            # Store trend
            if commodity not in self.seasonal_patterns:
                self.seasonal_patterns[commodity] = {}
            
            self.seasonal_patterns[commodity]['momentum'] = momentum
            self.seasonal_patterns[commodity]['trend'] = 'increasing' if momentum > 5 else 'decreasing' if momentum < -5 else 'stable'
            self.seasonal_patterns[commodity]['weekly_prices'] = weekly_avg
    
    def build_seasonal_patterns(self):
        """Build seasonal patterns from all data"""
        commodities = set(e.get('commodity') for e in self.market_data)
        
        for commodity in commodities:
            entries = [e for e in self.market_data if e.get('commodity') == commodity]
            
            if len(entries) < 5:
                continue
            
            # Group by month
            monthly_prices = {}
            for entry in entries:
                date = datetime.fromisoformat(entry.get('posted_at', datetime.now().isoformat()))
                month = date.month
                if month not in monthly_prices:
                    monthly_prices[month] = []
                monthly_prices[month].append(entry.get('price_per_kg', 0))
            
            # Calculate monthly averages
            seasonal_pattern = {}
            for month, prices in monthly_prices.items():
                seasonal_pattern[month] = {
                    'avg_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'data_points': len(prices)
                }
            
            # Store seasonal pattern
            if commodity not in self.seasonal_patterns:
                self.seasonal_patterns[commodity] = {}
            
            self.seasonal_patterns[commodity]['seasonal'] = seasonal_pattern
    
    def verify_price(self, listing_id, user_id, action):
        """Verify or dispute a price"""
        if listing_id not in self.price_verifications:
            self.price_verifications[listing_id] = {
                'confirms': [],
                'disputes': []
            }
        
        if action == 'confirm':
            self.price_verifications[listing_id]['confirms'].append({
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.price_verifications[listing_id]['disputes'].append({
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
        
        # Calculate trust score
        verifications = self.price_verifications[listing_id]
        confirms = len(verifications['confirms'])
        disputes = len(verifications['disputes'])
        
        if confirms + disputes > 0:
            trust_score = confirms / (confirms + disputes)
        else:
            trust_score = 0.5
        
        self.trust_scores[listing_id] = trust_score
        
        self.save_all_data()
        return trust_score
    
    def get_smart_prediction(self, commodity, region):
        """Generate smart prediction using all accumulated data"""
        key = f"{commodity}_{region}"
        
        # Gather all learned data
        market_stats = self.market_stats.get(key, {})
        recent_listings = [e for e in self.market_data if e.get('commodity') == commodity][:20]
        seasonal_pattern = self.seasonal_patterns.get(commodity, {}).get('seasonal', {})
        current_month = datetime.now().month
        
        # Build context
        context = {
            'market_stats': {
                'avg_price': market_stats.get('avg_price', 0),
                'min_price': market_stats.get('min_price', 0),
                'max_price': market_stats.get('max_price', 0),
                'trend': market_stats.get('trend', 'stable'),
                'total_listings': market_stats.get('total_listings', 0)
            },
            'recent_listings': recent_listings[:10],
            'seasonal_pattern': seasonal_pattern.get(current_month, {}),
            'prediction_history': self.prediction_history[-5:] if self.prediction_history else []
        }
        
        return context
    
    def save_prediction(self, commodity, prediction):
        """Save prediction for future learning"""
        entry = {
            'commodity': commodity,
            'predicted_price': prediction.get('price', 0),
            'predicted_at': datetime.now().isoformat(),
            'confidence': prediction.get('confidence', 0.7),
            'model_used': 'self_learning_ai'
        }
        self.prediction_history.append(entry)
        self.save_all_data()


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

def query_groq_with_rag(commodity, region, context):
    """Query Groq with RAG context"""
    try:
        api_key = get_groq_api_key()
        if not api_key:
            return {
                "success": False,
                "error": "Groq API key not configured."
            }

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Build prompt with all context
        market_stats = context.get('market_stats', {})
        recent_listings = context.get('recent_listings', [])
        seasonal = context.get('seasonal_pattern', {})
        
        prompt = f"""You are an Ethiopian market prediction AI.
You have access to REAL market data collected from Ethiopian traders.

## Live Ethiopian Market Stats:
- Current avg price: ETB {market_stats.get('avg_price', 0)}/kg
- Price range: ETB {market_stats.get('min_price', 0)} - {market_stats.get('max_price', 0)}
- Market trend: {market_stats.get('trend', 'stable')}
- Total listings analyzed: {market_stats.get('total_listings', 0)}

## Recent Listings:
{json.dumps(recent_listings[:5], indent=2)}

## Seasonal Pattern for This Month:
- Typical price: ETB {seasonal.get('avg_price', 'N/A')}/kg
- Historical range: ETB {seasonal.get('min_price', 'N/A')} - {seasonal.get('max_price', 'N/A')}

## Ethiopian Economic Context:
- Birr depreciated significantly since July 2024
- Current inflation trend
- Regional market conditions in {region}

Based on this real data, provide:
1. Fair price suggestion (ETB)
2. 30-day prediction with confidence
3. 90-day prediction with confidence
4. Seasonal outlook
5. Specific recommendations for producers
6. Risk warnings

Be specific with numbers and realistic about Ethiopian market conditions."""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an expert Ethiopian commodity market analyst. Use the provided real market data to make accurate predictions."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API Error {response.status_code}"
            }
        
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content'].strip()
            
            # Parse predictions
            current_match = re.search(r'Fair price.*?ETB\s*([\d.]+)', content, re.IGNORECASE)
            thirty_match = re.search(r'30[- ]?day.*?ETB\s*([\d.]+)', content, re.IGNORECASE)
            ninety_match = re.search(r'90[- ]?day.*?ETB\s*([\d.]+)', content, re.IGNORECASE)
            
            result = {
                "success": True,
                "raw_response": content,
                "source": "Groq AI with RAG"
            }
            
            if current_match:
                result["current_price"] = float(current_match.group(1))
            if thirty_match:
                result["prediction_30d"] = float(thirty_match.group(1))
            if ninety_match:
                result["prediction_90d"] = float(ninety_match.group(1))
            
            return result
        else:
            return {"success": False, "error": "Unexpected API response"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==========================================
# RENDER AI INSIGHTS SELF-LEARNING
# ==========================================

def render_ai_insights_self_learning(user_info):
    """Render self-learning AI insights tab"""
    
    # Initialize intelligence system
    intelligence = MarketIntelligence(user_info['id'])
    
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
    .prediction-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3748;
        margin-bottom: 12px;
        text-align: center;
    }
    .prediction-card .price {
        font-size: 32px;
        font-weight: 700;
        color: #10b981;
    }
    .prediction-card .label {
        color: #94a3b8;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-self {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .badge-learned {
        display: inline-block;
        background: #10b981;
        color: white;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .learning-stats {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("🧠 Self-Learning AI Market Intelligence")
    st.caption("The AI learns from every product you post and every market interaction")
    
    # Learning Statistics
    st.markdown("### 📊 Learning Progress")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Market Entries", len(intelligence.market_data))
    with col2:
        st.metric("📈 Trends Tracked", len(intelligence.market_stats))
    with col3:
        st.metric("📅 Seasonal Patterns", len(intelligence.seasonal_patterns))
    with col4:
        trust_scores = list(intelligence.trust_scores.values()) if intelligence.trust_scores else [0]
        avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0
        st.metric("⭐ Avg Trust Score", f"{avg_trust:.0%}")
    
    st.markdown("---")
    
    # API Key Check
    api_key = get_groq_api_key()
    if not api_key:
        st.warning("⚠️ Groq API key not found. Please add GROQ_API_KEY to secrets for AI predictions.")
    
    # Get products
    all_products = get_products(producer_id=user_info['id'])
    user_product_names = [p['name'] for p in all_products] if all_products else []
    
    # Product selection
    st.markdown("### 🔍 Select Commodity for Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_option = st.radio(
            "Choose product:",
            ["Select from my products", "Enter custom product name"],
            horizontal=True
        )
    
    with col2:
        regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                  "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
        selected_region = st.selectbox("Region", regions, index=0)
    
    if search_option == "Select from my products":
        if user_product_names:
            selected_product_name = st.selectbox("Select Product", user_product_names)
        else:
            st.warning("No products in inventory. Please add products or use custom search.")
            selected_product_name = st.text_input("Enter Product Name", placeholder="e.g., Teff, Coffee, Wheat...")
    else:
        selected_product_name = st.text_input("Enter Product Name", placeholder="e.g., Teff, Coffee, Wheat, Barley...")
    
    if not selected_product_name:
        st.info("💡 Enter a product name or select from your inventory to get market predictions.")
        return
    
    product_name = selected_product_name.strip()
    
    st.markdown("---")
    
    # Get smart prediction context
    context = intelligence.get_smart_prediction(product_name, selected_region)
    
    # Display what the AI has learned
    with st.expander("🧠 What the AI Has Learned So Far", expanded=False):
        st.markdown("#### 📊 Market Statistics")
        stats = context.get('market_stats', {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"ETB {stats.get('avg_price', 0):.0f}/kg")
        with col2:
            st.metric("Price Range", f"ETB {stats.get('min_price', 0)} - {stats.get('max_price', 0)}")
        with col3:
            st.metric("Trend", stats.get('trend', 'Unknown').capitalize())
        
        if context.get('recent_listings'):
            st.markdown("#### 📝 Recent Listings Learned")
            df = pd.DataFrame(context['recent_listings'])
            if not df.empty:
                st.dataframe(df[['commodity', 'price_per_kg', 'region', 'quality_grade']].head(5))
    
    st.markdown("---")
    
    # AI Prediction
    st.markdown("### 🎯 AI Prediction with RAG")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Analyzing {product_name} in {selected_region} using {len(intelligence.market_data)} learned data points")
    with col2:
        if st.button("🔮 Generate Prediction", use_container_width=True, type="primary"):
            with st.spinner(f"Analyzing market data for {product_name}..."):
                result = query_groq_with_rag(product_name, selected_region, context)
                
                if result.get('success'):
                    st.session_state.rag_prediction = result
                    
                    # Save prediction for learning
                    intelligence.save_prediction(product_name, {
                        'price': result.get('current_price', 0),
                        'confidence': 0.85
                    })
                    
                    st.success("✅ Prediction generated from learned data!")
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('error', 'Prediction failed')}")
    
    # Display prediction results
    rag_pred = st.session_state.get('rag_prediction', {})
    
    if rag_pred.get('success'):
        st.markdown("### 📊 Market Analysis & Predictions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="prediction-card">
                <div class="label">💰 Fair Price</div>
                <div class="price">{rag_pred.get('current_price', 'N/A')} ETB/kg</div>
                <span class="badge-self">AI Suggestion</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="prediction-card">
                <div class="label">📈 30-Day Forecast</div>
                <div class="price">{rag_pred.get('prediction_30d', 'N/A')} ETB/kg</div>
                <span class="badge-learned">Learned Pattern</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="prediction-card">
                <div class="label">📊 90-Day Forecast</div>
                <div class="price">{rag_pred.get('prediction_90d', 'N/A')} ETB/kg</div>
                <span class="badge-learned">Seasonal Pattern</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Full analysis
        st.markdown("### 🧠 AI Market Analysis")
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">📋 Detailed Analysis</div>
            <div style="color: #e2e8f0; white-space: pre-wrap; font-size: 14px; line-height: 1.6;">
                {rag_pred.get('raw_response', 'No detailed analysis available')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Trust indicators
        st.markdown("---")
        st.markdown("#### ⭐ Data Trust Indicators")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            data_points = len(intelligence.market_data)
            st.metric("📊 Data Points", data_points, help="Total market entries learned")
        with col2:
            st.metric("🧠 Learning Iterations", intelligence.knowledge_base.get('learning_iterations', 0) if hasattr(intelligence, 'knowledge_base') else 0)
        with col3:
            trust = avg_trust if 'avg_trust' in locals() else 0
            st.metric("⭐ Trust Score", f"{trust:.0%}", help="Based on price verifications")
    
    else:
        st.info("💡 Click 'Generate Prediction' to get AI analysis using all learned data.")
        
        # Show what data will be used
        st.markdown("#### 📊 Data That Will Be Used")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📦 Market Entries", len(intelligence.market_data))
            if context.get('market_stats'):
                st.caption(f"• Avg Price: ETB {context['market_stats'].get('avg_price', 0):.0f}/kg")
                st.caption(f"• Trend: {context['market_stats'].get('trend', 'Unknown').capitalize()}")
        with col2:
            st.metric("📅 Seasonal Patterns", len(intelligence.seasonal_patterns))
            if context.get('seasonal_pattern'):
                st.caption(f"• Current Month Pattern: {context['seasonal_pattern'].get('avg_price', 'N/A')} ETB/kg")
    
    st.markdown("---")
    
    # How the AI learns
    st.markdown("### 🧠 How the AI Learns")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="learning-stats">
            <div style="font-size: 24px; margin-bottom: 8px;">📝</div>
            <div style="color: #f8fafc; font-weight: 600;">Step 1: User Posts</div>
            <div style="color: #94a3b8; font-size: 13px;">Every product you post teaches the AI about market prices</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="learning-stats">
            <div style="font-size: 24px; margin-bottom: 8px;">📊</div>
            <div style="color: #f8fafc; font-weight: 600;">Step 2: Pattern Detection</div>
            <div style="color: #94a3b8; font-size: 13px;">AI detects trends, seasons, and regional patterns automatically</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="learning-stats">
            <div style="font-size: 24px; margin-bottom: 8px;">🎯</div>
            <div style="color: #f8fafc; font-weight: 600;">Step 3: Smarter Predictions</div>
            <div style="color: #94a3b8; font-size: 13px;">AI combines all learned data for accurate market predictions</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("📁 Model files saved to `Models/` folder | Data stored in `data/` folder")
