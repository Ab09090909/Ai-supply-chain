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

def query_groq_api(product_name, region="Addis Ababa"):
    """Query the Groq API for current product price in Ethiopia with detailed response."""
    try:
        api_key = get_groq_api_key()
        if not api_key:
            return {
                "success": False,
                "error": "Groq API key not configured. Please add GROQ_API_KEY to secrets."
            }

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Better prompt for detailed response
        prompt = f"""Provide the current market price information for {product_name} in {region}, Ethiopia.

Please provide:
1. Current price in ETB per kilogram
2. Price range (lowest to highest)
3. Market trend (increasing, stable, or decreasing)
4. Demand level (high, medium, or low)
5. Brief market insight

Format your response as:
Price: [number] ETB/kg
Range: [min] - [max] ETB/kg
Trend: [trend]
Demand: [level]
Insight: [brief market insight]"""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a market price analyst for Ethiopian agricultural products. Provide accurate, current market prices with insights."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error'].get('message', error_msg)
            except:
                pass
            
            return {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code
            }
        
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content'].strip()
            
            # Parse the detailed response
            price_match = re.search(r'Price:\s*([\d.]+)', content)
            range_match = re.search(r'Range:\s*([\d.]+)\s*-\s*([\d.]+)', content)
            trend_match = re.search(r'Trend:\s*(\w+)', content, re.IGNORECASE)
            demand_match = re.search(r'Demand:\s*(\w+)', content, re.IGNORECASE)
            insight_match = re.search(r'Insight:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
            
            result = {
                "success": True,
                "raw_response": content,
                "source": "Groq API"
            }
            
            if price_match:
                result["price"] = float(price_match.group(1))
            else:
                # Try to find any number
                all_numbers = re.findall(r'(\d+\.?\d*)', content)
                if all_numbers:
                    for num in all_numbers:
                        num_float = float(num)
                        if 1 <= num_float <= 10000:
                            result["price"] = num_float
                            break
            
            if range_match:
                result["min_price"] = float(range_match.group(1))
                result["max_price"] = float(range_match.group(2))
            
            if trend_match:
                result["trend"] = trend_match.group(1).lower()
            
            if demand_match:
                result["demand"] = demand_match.group(1).lower()
            
            if insight_match:
                result["insight"] = insight_match.group(1).strip()
            
            result["unit"] = "kg"
            
            return result
        else:
            return {
                "success": False,
                "error": "Unexpected API response format",
                "raw_data": data
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error. Please check your internet."}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# SUPABASE FUNCTIONS
# ==========================================

def save_training_data_supabase(user_id, data):
    """Save AI training data to Supabase."""
    try:
        if supabase is None:
            return False, "Database connection failed"
        
        record = {
            'user_id': user_id,
            'product_name': data.get('product_name'),
            'price': data.get('price'),
            'market_price': data.get('market_price'),
            'demand_score': data.get('demand_score', 70),
            'seasonal_factor': data.get('seasonal_factor', 1.0),
            'region_factor': data.get('region_factor', 1.0),
            'trend_factor': data.get('trend_factor', 1.0),
            'predicted_price': data.get('predicted_price'),
            'actual_price': data.get('actual_price'),
            'data_source': data.get('data_source', 'groq_api'),
            'region': data.get('region', 'Addis Ababa')
        }
        
        response = supabase.table('ai_training_data').insert(record).execute()
        return True, "Training data saved to Supabase"
    except Exception as e:
        return False, str(e)

def get_training_data_supabase(user_id, limit=1000):
    """Retrieve AI training data from Supabase."""
    try:
        if supabase is None:
            return []
        
        response = supabase.table('ai_training_data')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        return []

def get_product_market_data(product_name, region="Addis Ababa"):
    """Get stored market data for a product from Supabase."""
    try:
        if supabase is None:
            return None
        
        response = supabase.table('ai_training_data')\
            .select('*')\
            .eq('product_name', product_name)\
            .eq('region', region)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        return None

# ==========================================
# SELF-LEARNING AI SYSTEM
# ==========================================

class SelfLearningAIInsights:
    """Self-learning AI system with Supabase storage and Groq integration"""
    
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
                    'accuracy_score': 0,
                    'groq_queries': []
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
                'accuracy_score': 0,
                'groq_queries': []
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
                self.train_with_supabase_data()
                return True
        except Exception as e:
            return False
    
    def train_with_supabase_data(self):
        """Train model using data from Supabase"""
        try:
            training_data = get_training_data_supabase(self.user_id)
            if len(training_data) < 5:
                training_data = self.knowledge_base.get('training_data', [])
            
            if len(training_data) > 5:
                self.train_model(training_data)
                return True
            else:
                synthetic_data = self.generate_synthetic_data()
                self.train_model(synthetic_data)
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
        products = ['Teff', 'Wheat', 'Coffee', 'Milk', 'Onion', 'Tomato', 'Beef']
        
        for product in products:
            for i in range(5):
                base_price = random.uniform(50, 300)
                data = {
                    'product_name': product,
                    'price': base_price,
                    'demand_score': random.uniform(30, 95),
                    'seasonal_factor': random.uniform(0.7, 1.3),
                    'region_factor': random.uniform(0.8, 1.2),
                    'trend_factor': random.uniform(0.9, 1.1),
                    'predicted_price': base_price * random.uniform(0.85, 1.25)
                }
                synthetic_data.append(data)
        
        return synthetic_data
    
    def save_model(self):
        """Save model to disk (GitHub Models folder)"""
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
    
    def query_groq_for_price(self, product_name, region="Addis Ababa"):
        """Query Groq API for product price and store results"""
        result = query_groq_api(product_name, region)
        
        if result.get('success'):
            if 'groq_queries' not in self.knowledge_base:
                self.knowledge_base['groq_queries'] = []
            
            self.knowledge_base['groq_queries'].append({
                'product': product_name,
                'region': region,
                'price': result.get('price'),
                'unit': result.get('unit', 'kg'),
                'trend': result.get('trend', 'N/A'),
                'demand': result.get('demand', 'N/A'),
                'insight': result.get('insight', 'N/A'),
                'timestamp': datetime.now().isoformat(),
                'raw_response': result.get('raw_response')
            })
            
            save_training_data_supabase(self.user_id, {
                'product_name': product_name,
                'price': result.get('price'),
                'market_price': result.get('price'),
                'data_source': 'groq_api',
                'region': region,
                'demand_score': 70,
                'predicted_price': result.get('price')
            })
            
            self.save_knowledge_base()
            return result
        else:
            return result
    
    def predict_price(self, product_data):
        """Predict optimal price using AI model"""
        try:
            market_data = get_product_market_data(
                product_data.get('product', ''),
                product_data.get('region', 'Addis Ababa')
            )
            
            if market_data:
                market_price = market_data.get('market_price')
            else:
                market_price = product_data.get('current_price', 100)
            
            features = [
                market_price,
                self.calculate_demand_score(product_data),
                product_data.get('seasonal_factor', 1.0),
                product_data.get('region_factor', 1.0),
                self.calculate_trend_factor(product_data)
            ]
            
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            predicted_price = self.model.predict(X_scaled)[0]
            
            min_price = product_data.get('min_price', 50) * 0.7
            max_price = product_data.get('max_price', 300) * 1.3
            predicted_price = max(min_price, min(predicted_price, max_price))
            
            product_name = product_data.get('product', 'Unknown')
            self.knowledge_base['predictions'][product_name] = {
                'predicted_price': round(predicted_price, 2),
                'current_price': product_data.get('current_price', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.save_knowledge_base()
            return round(predicted_price, 2)
            
        except Exception as e:
            return round(product_data.get('current_price', 100) * random.uniform(0.95, 1.15), 2)
    
    def calculate_demand_score(self, data):
        """Calculate demand score for a product"""
        base_score = {
            'high': 85,
            'medium': 60,
            'low': 35
        }.get(data.get('demand', 'medium'), 50)
        
        avg_price = data.get('avg_price', 100)
        current_price = data.get('current_price', 100)
        price_ratio = current_price / avg_price if avg_price > 0 else 1
        
        if price_ratio < 0.8:
            base_score += 10
        elif price_ratio > 1.2:
            base_score -= 10
        
        return max(0, min(100, base_score))
    
    def calculate_trend_factor(self, data):
        """Calculate trend factor"""
        trend = data.get('trend', 'stable')
        if trend == 'increasing':
            return 1.1
        elif trend == 'decreasing':
            return 0.9
        else:
            return 1.0
    
    def get_market_insights(self, product_name, region="Addis Ababa"):
        """Get comprehensive market insights for a product"""
        # Try Groq API
        groq_result = self.query_groq_for_price(product_name, region)
        
        if groq_result.get('success'):
            market_price = groq_result.get('price')
            market_data = {
                'product': product_name,
                'current_price': market_price,
                'avg_price': market_price * 0.95,
                'min_price': groq_result.get('min_price', market_price * 0.8),
                'max_price': groq_result.get('max_price', market_price * 1.2),
                'trend': groq_result.get('trend', 'stable'),
                'demand': groq_result.get('demand', 'medium'),
                'insight': groq_result.get('insight', 'Market data from Groq AI'),
                'unit': groq_result.get('unit', 'kg'),
                'source': 'Groq API'
            }
        else:
            # Fallback to local data
            scraper = EthiopianMarketScraper()
            market_data = scraper.get_current_price(product_name)
            market_data['insight'] = 'Estimated market data (Groq API unavailable)'
        
        predicted_price = self.predict_price({**market_data, 'region': region})
        demand_forecast = self.forecast_demand(product_name, region)
        price_recommendations = self.get_price_recommendations(market_data)
        
        return {
            'market_data': market_data,
            'predicted_price': predicted_price,
            'demand_forecast': demand_forecast,
            'price_recommendations': price_recommendations,
            'confidence_score': self.calculate_confidence(market_data),
            'groq_source': groq_result.get('success', False),
            'groq_insight': market_data.get('insight', '')
        }
    
    def forecast_demand(self, product_name, region="Addis Ababa"):
        """Forecast demand for a product"""
        demand_patterns = self.knowledge_base.get('demand_patterns', {})
        
        if product_name in demand_patterns:
            history = demand_patterns[product_name]
            avg_demand = sum(history) / len(history) if history else 100
            trend = 'increasing' if len(history) > 1 and history[-1] > history[-2] else 'decreasing'
        else:
            base_demand = {
                'Grains': 150, 'Vegetables': 120, 'Fruits': 100,
                'Dairy': 130, 'Meat': 110, 'Coffee': 100
            }
            avg_demand = base_demand.get(product_name, 100)
            trend = 'stable'
        
        current_month = datetime.now().month
        seasonal_factors = {
            1: 1.1, 2: 1.0, 3: 0.9, 4: 0.9, 5: 1.0,
            6: 1.1, 7: 1.2, 8: 1.2, 9: 1.0, 10: 0.9,
            11: 0.8, 12: 1.0
        }
        seasonal_factor = seasonal_factors.get(current_month, 1.0)
        
        region_factors = {
            'Addis Ababa': 1.3, 'Oromia': 1.0, 'Amhara': 0.95,
            'Tigray': 0.9, 'SNNP': 0.85, 'Sidama': 0.9
        }
        region_factor = region_factors.get(region, 1.0)
        
        daily_demand = avg_demand * seasonal_factor * region_factor
        
        return {
            'daily_demand': round(daily_demand, 1),
            'weekly_demand': round(daily_demand * 7, 1),
            'monthly_demand': round(daily_demand * 30, 1),
            'trend': trend,
            'seasonal_factor': seasonal_factor,
            'region_factor': region_factor,
            'confidence': 0.85 if product_name in demand_patterns else 0.65
        }
    
    def get_price_recommendations(self, market_data):
        """Get price recommendations based on market data"""
        current_price = market_data.get('current_price', 100)
        avg_price = market_data.get('avg_price', 100)
        trend = market_data.get('trend', 'stable')
        demand = market_data.get('demand', 'medium')
        
        if trend == 'increasing' and demand == 'high':
            recommendation = 'Increase Price'
            recommended_price = current_price * 1.12
        elif trend == 'decreasing' and demand == 'medium':
            recommendation = 'Decrease Price'
            recommended_price = current_price * 0.92
        elif trend == 'volatile':
            recommendation = 'Hold and Monitor'
            recommended_price = current_price
        else:
            recommendation = 'Maintain Price'
            recommended_price = current_price * 1.02
        
        min_price = market_data.get('min_price', 50)
        max_price = market_data.get('max_price', 300)
        recommended_price = max(min_price, min(recommended_price, max_price))
        
        return {
            'recommendation': recommendation,
            'current_price': current_price,
            'recommended_price': round(recommended_price, 2),
            'market_average': avg_price,
            'reasoning': f"Based on {trend} trend and {demand} demand",
            'confidence': 0.88 if demand != 'medium' else 0.75
        }
    
    def calculate_confidence(self, market_data):
        """Calculate confidence score for predictions"""
        base_confidence = 0.7
        
        if market_data.get('source') == 'Groq API':
            base_confidence += 0.15
        elif market_data.get('source') == 'Ethiopian Market Data':
            base_confidence += 0.1
        
        iterations = self.knowledge_base.get('learning_iterations', 0)
        base_confidence += min(iterations / 1000, 0.15)
        
        accuracy = self.knowledge_base.get('accuracy_score', 0.5)
        base_confidence += (accuracy - 0.5) * 0.3
        
        return min(0.98, max(0.5, base_confidence))


# ==========================================
# ETHIOPIAN MARKET SCRAPER (FALLBACK)
# ==========================================

class EthiopianMarketScraper:
    """Fallback Ethiopian market data when Groq is unavailable"""
    
    def __init__(self):
        self.product_prices = {
            'Teff': {'min': 80, 'max': 160, 'avg': 120, 'trend': 'increasing', 'demand': 'high'},
            'Wheat': {'min': 45, 'max': 80, 'avg': 60, 'trend': 'stable', 'demand': 'high'},
            'Coffee': {'min': 200, 'max': 450, 'avg': 320, 'trend': 'increasing', 'demand': 'high'},
            'Milk': {'min': 60, 'max': 100, 'avg': 75, 'trend': 'increasing', 'demand': 'high'},
            'Beef': {'min': 400, 'max': 650, 'avg': 520, 'trend': 'increasing', 'demand': 'high'},
            'Onion': {'min': 25, 'max': 50, 'avg': 35, 'trend': 'volatile', 'demand': 'high'},
            'Tomato': {'min': 30, 'max': 60, 'avg': 42, 'trend': 'volatile', 'demand': 'high'},
            'Potato': {'min': 35, 'max': 70, 'avg': 50, 'trend': 'increasing', 'demand': 'high'},
        }
    
    def get_current_price(self, product_name):
        """Get current price for a product"""
        closest_match = None
        for key in self.product_prices:
            if product_name.lower() in key.lower() or key.lower() in product_name.lower():
                closest_match = key
                break
        
        if closest_match:
            price_data = self.product_prices[closest_match]
            return {
                'product': closest_match,
                'current_price': round(random.uniform(price_data['min'], price_data['max']), 2),
                'min_price': price_data['min'],
                'max_price': price_data['max'],
                'avg_price': price_data['avg'],
                'trend': price_data['trend'],
                'demand': price_data['demand'],
                'unit': 'kg',
                'source': 'Fallback Data'
            }
        else:
            return {
                'product': product_name,
                'current_price': round(random.uniform(50, 200), 2),
                'min_price': 50,
                'max_price': 200,
                'avg_price': 125,
                'trend': 'stable',
                'demand': 'medium',
                'unit': 'kg',
                'source': 'Estimated'
            }


# ==========================================
# RENDER AI INSIGHTS TAB
# ==========================================

def render_ai_insights(user_info, ai):
    """Render AI Insights tab with Groq API integration"""
    
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
    .insight-card .trend-up { color: #10b981; }
    .insight-card .trend-down { color: #ef4444; }
    .insight-card .trend-neutral { color: #f59e0b; }
    .groq-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("🤖 AI-Powered Market Insights")
    st.caption("Real-time Ethiopian market analysis with Groq AI integration")
    
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
        st.warning("⚠️ Groq API key not found. Please add GROQ_API_KEY to secrets.")
        st.info("Format: GROQ_API_KEY = 'your_key_here'")
    
    # Products
    all_products = get_products(producer_id=user_info['id'])
    if not all_products:
        st.warning("⚠️ Please add products first")
        return
    
    # Selection
    product_names = {p['id']: p['name'] for p in all_products}
    selected_prod_id = st.selectbox("Select Product", list(product_names.keys()), format_func=lambda x: product_names[x])
    selected_product = next((p for p in all_products if p['id'] == selected_prod_id), None)
    if not selected_product:
        return
    
    product_name = selected_product.get('name', '')
    
    regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
              "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
    selected_region = st.selectbox("Region", regions, index=0)
    
    st.markdown("---")
    
    # Query button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🔍 Get Price for {product_name}")
        st.caption(f"Query Groq AI for current {product_name} prices in {selected_region}")
    with col2:
        if st.button("🚀 Query Groq", use_container_width=True, type="primary"):
            with st.spinner("Querying Groq AI..."):
                result = ai_insights.query_groq_for_price(product_name, selected_region)
                if result.get('success'):
                    st.success(f"✅ Price fetched from Groq AI!")
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
                    if result.get('raw_response'):
                        st.caption(f"Response: {result.get('raw_response')}")
    
    # Get insights (always shows local data if Groq fails)
    insights = ai_insights.get_market_insights(product_name, selected_region)
    market_data = insights.get('market_data', {})
    
    st.markdown("### 📊 Market Analysis")
    
    if insights.get('groq_source'):
        st.markdown('<span class="groq-badge">🤖 Groq AI</span>', unsafe_allow_html=True)
        
        # Show AI Insight
        if insights.get('groq_insight'):
            st.markdown(f"""
            <div class="insight-text">
                💡 <strong>AI Insight:</strong> {insights.get('groq_insight')}
            </div>
            """, unsafe_allow_html=True)
    
    current_price = selected_product.get('price', 0)
    market_avg = market_data.get('avg_price', 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Your Price", f"{current_price:.0f} ETB")
    with col2:
        st.metric("📊 Market Avg", f"{market_avg:.0f} ETB")
    with col3:
        diff = current_price - market_avg
        pct = (diff / market_avg * 100) if market_avg > 0 else 0
        st.metric("📈 Difference", f"{diff:+.0f} ETB", delta=f"{pct:+.1f}%")
    
    # Market Details
    if market_data.get('min_price') and market_data.get('max_price'):
        st.caption(f"📊 Price Range: {market_data.get('min_price', 0):.0f} - {market_data.get('max_price', 0):.0f} ETB/kg")
    
    if market_data.get('trend'):
        trend_emoji = "📈" if market_data.get('trend') == 'increasing' else "📉" if market_data.get('trend') == 'decreasing' else "➡️"
        st.caption(f"{trend_emoji} Trend: {market_data.get('trend', 'N/A').capitalize()}")
    
    if market_data.get('demand'):
        demand_emoji = "🔥" if market_data.get('demand') == 'high' else "📊" if market_data.get('demand') == 'medium' else "❄️"
        st.caption(f"{demand_emoji} Demand: {market_data.get('demand', 'N/A').capitalize()}")
    
    st.markdown("---")
    
    # Recommendation
    price_rec = insights.get('price_recommendations', {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">🎯 Recommendation</div>
            <div class="value">{price_rec.get('recommendation', 'Maintain Price')}</div>
            <div class="sub">Recommended: <strong>{price_rec.get('recommended_price', current_price):.0f} ETB</strong></div>
            <div class="sub">{price_rec.get('reasoning', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        rec_price = price_rec.get('recommended_price', current_price)
        pct_change = ((rec_price - current_price) / current_price * 100) if current_price > 0 else 0
        color = "#10b981" if pct_change > 0 else "#ef4444"
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">📊 Impact</div>
            <div class="value" style="color:{color}">{pct_change:+.1f}%</div>
            <div class="sub">Current: {current_price:.0f} → Recommended: {rec_price:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Demand
    demand = insights.get('demand_forecast', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Daily", f"{demand.get('daily_demand', 0):.0f}")
    with col2:
        st.metric("📅 Weekly", f"{demand.get('weekly_demand', 0):.0f}")
    with col3:
        st.metric("📅 Monthly", f"{demand.get('monthly_demand', 0):.0f}")
    
    st.markdown("---")
    
    # Stock
    stock = selected_product.get('quantity', 0)
    daily = demand.get('daily_demand', 1)
    days = stock / daily if daily > 0 else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        status = "✅ Healthy" if days > 14 else "⚠️ Low" if days > 7 else "🔴 Critical"
        color = "#10b981" if days > 14 else "#f59e0b" if days > 7 else "#ef4444"
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">📦 Stock</div>
            <div class="value" style="color:{color}">{status}</div>
            <div class="sub">{days:.1f} days remaining</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if days < 7:
            st.markdown(f"""
            <div class="insight-card">
                <div class="title">🔄 Restock</div>
                <div class="value" style="color:#ef4444">RESTOCK NOW</div>
                <div class="sub">Order: {int(daily * 14)} units</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-card">
                <div class="title">🔄 Restock</div>
                <div class="value" style="color:#10b981">Adequate</div>
                <div class="sub">Restock in {int(days - 7)} days</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Training
    st.markdown("### 🧠 AI Training")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Train Model", use_container_width=True):
            training_data = get_training_data_supabase(user_info['id'])
            if training_data:
                success = ai_insights.train_model(training_data)
            else:
                success = ai_insights.train_with_supabase_data()
            if success:
                st.success("✅ Model trained!")
                st.rerun()
    
    with col2:
        if st.button("📊 Performance", use_container_width=True):
            acc = ai_insights.knowledge_base.get('accuracy_score', 0)
            samples = len(ai_insights.knowledge_base.get('training_data', []))
            st.info(f"Accuracy: {acc*100:.1f}%")
            st.info(f"Samples: {samples}")
    
    with col3:
        if st.button("💾 Save Model", use_container_width=True):
            if ai_insights.save_model():
                st.success("✅ Saved to Models/ folder!")
    
    st.caption("📁 Models saved to `Models/` folder")
