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
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

from utils.db_helpers import get_products, get_user_by_id, get_orders, supabase

# ==========================================
# GROQ API FOR RECOMMENDATIONS ONLY
# ==========================================

def get_groq_api_key():
    """Get Groq API key from secrets"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("groq_api_key") or st.secrets.get("GROQ_KEY")
        return api_key
    except Exception as e:
        return None

def query_groq_recommendations(product_name, user_behavior, market_data):
    """Query Groq for product recommendations based on user behavior and market data"""
    try:
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
        
        prompt = f"""Based on user behavior and market data, recommend products.

User Behavior:
- Products posted: {json.dumps(user_behavior.get('products', []), indent=2)}
- Buy/Sell patterns: {json.dumps(user_behavior.get('transactions', []), indent=2)}
- Preferred categories: {json.dumps(user_behavior.get('categories', []), indent=2)}
- Average price range: {user_behavior.get('avg_price', 0)} ETB

Market Data:
- Popular products: {json.dumps(market_data.get('popular', []), indent=2)}
- Trending products: {json.dumps(market_data.get('trending', []), indent=2)}
- High demand products: {json.dumps(market_data.get('high_demand', []), indent=2)}

Current Product: {product_name}

Provide 5 personalized product recommendations with reasons.
Format as:
1. Product Name - Reason - Estimated Price Range"""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a product recommendation system. Analyze user behavior and market trends to provide relevant recommendations."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
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
            
            # Parse recommendations
            recommendations = []
            lines = content.split('\n')
            
            for line in lines:
                if re.match(r'^\d+\.', line):
                    parts = line.split('-')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        reason = parts[1].strip() if len(parts) > 1 else "Recommended based on your activity"
                        price_match = re.search(r'([\d.]+)\s*-\s*([\d.]+)', line)
                        if price_match:
                            price_min = float(price_match.group(1))
                            price_max = float(price_match.group(2))
                        else:
                            price_min = None
                            price_max = None
                        
                        recommendations.append({
                            'name': name.replace('^d+\.', '').strip(),
                            'reason': reason,
                            'price_min': price_min,
                            'price_max': price_max
                        })
            
            return {
                "success": True,
                "recommendations": recommendations,
                "raw_response": content,
                "source": "Groq API"
            }
        else:
            return {
                "success": False,
                "error": "Unexpected API response format",
                "fallback_used": True
            }
            
    except Exception as e:
        return {"success": False, "error": str(e), "fallback_used": True}

# ==========================================
# PRICE PREDICTION SYSTEM (NO BENCHMARKS)
# ==========================================

class PricePredictionSystem:
    """Price prediction system based solely on user posted products and transactions"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.data_dir = "data"
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.product_data = []
        self.transaction_data = []
        self.prediction_history = []
        self.load_data()
        
    def load_data(self):
        """Load product data from database"""
        try:
            # Get user's products
            products = get_products(producer_id=self.user_id)
            self.product_data = products if products else []
            
            # Get user's orders/transactions
            orders = get_orders(self.user_id, 'producer', limit=100)
            self.transaction_data = orders if orders else []
            
            # Load prediction history
            pred_path = f"{self.data_dir}/predictions_{self.user_id}.json"
            if os.path.exists(pred_path):
                with open(pred_path, 'r') as f:
                    self.prediction_history = json.load(f)
            else:
                self.prediction_history = []
                
        except Exception as e:
            self.product_data = []
            self.transaction_data = []
            self.prediction_history = []
    
    def save_predictions(self):
        """Save prediction history"""
        try:
            with open(f"{self.data_dir}/predictions_{self.user_id}.json", 'w') as f:
                json.dump(self.prediction_history, f, indent=2)
        except Exception as e:
            pass
    
    def get_category_prices(self, product_name):
        """Get price data for similar products"""
        category = self.get_product_category(product_name)
        
        similar_prices = []
        for product in self.product_data:
            if product.get('category') == category and product.get('price', 0) > 0:
                similar_prices.append(product.get('price', 0))
        
        return similar_prices
    
    def get_product_category(self, product_name):
        """Get category for a product"""
        categories = {
            'Grains': ['teff', 'wheat', 'barley', 'maize', 'sorghum', 'millet'],
            'Vegetables': ['onion', 'tomato', 'cabbage', 'potato', 'carrot', 'garlic'],
            'Fruits': ['banana', 'mango', 'avocado', 'orange', 'papaya', 'apple'],
            'Dairy': ['milk', 'butter', 'cheese', 'yogurt'],
            'Meat': ['beef', 'chicken', 'mutton', 'goat', 'fish'],
            'Coffee': ['coffee'],
            'Other': ['honey', 'sesame', 'sugar', 'oil']
        }
        
        product_lower = product_name.lower().strip()
        for category, products in categories.items():
            if any(p in product_lower for p in products):
                return category
        return 'Other'
    
    def predict_price(self, product_name, current_price):
        """Predict fair price based on user's own data"""
        # Get similar products from same category
        similar_prices = self.get_category_prices(product_name)
        
        # Get transaction history for this product
        transaction_prices = []
        for trans in self.transaction_data:
            if trans.get('product_name', '').lower() == product_name.lower():
                if trans.get('total_amount', 0) > 0:
                    transaction_prices.append(trans.get('total_amount', 0))
        
        # Combine all price data
        all_prices = similar_prices + transaction_prices
        
        if all_prices:
            # Calculate statistics from user's own data
            avg_price = sum(all_prices) / len(all_prices)
            min_price = min(all_prices)
            max_price = max(all_prices)
            
            # Determine if price is fair
            if min_price <= current_price <= max_price:
                is_fair = "Yes"
                recommendation = "Maintain"
            elif current_price < min_price:
                is_fair = "No (Too Low)"
                recommendation = "Increase"
            else:
                is_fair = "No (Too High)"
                recommendation = "Decrease"
            
            # Confidence based on data points
            if len(all_prices) > 10:
                confidence = "HIGH"
            elif len(all_prices) > 5:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
            
            # Generate explanation
            explanation = self.generate_explanation(product_name, current_price, avg_price, min_price, max_price)
            
            prediction = {
                'is_fair': is_fair,
                'ideal_min': int(min_price * 0.9),
                'ideal_max': int(max_price * 0.9),
                'recommendation': recommendation,
                'confidence': confidence,
                'explanation': explanation,
                'data_points': len(all_prices)
            }
        else:
            # No data available
            prediction = {
                'is_fair': "Unknown",
                'ideal_min': None,
                'ideal_max': None,
                'recommendation': "Insufficient Data",
                'confidence': "LOW",
                'explanation': f"No price data available for {product_name} or similar products. Add more products or transactions to get predictions.",
                'data_points': 0
            }
        
        # Save to history
        self.prediction_history.append({
            'product': product_name,
            'current_price': current_price,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
        self.save_predictions()
        
        return prediction
    
    def generate_explanation(self, product_name, current_price, avg_price, min_price, max_price):
        """Generate explanation for prediction"""
        if avg_price == 0:
            return f"No price data available for {product_name} or similar products."
        
        if current_price < avg_price * 0.8:
            return f"Your price is significantly below the average ({avg_price:.0f} ETB) for similar products. Consider increasing to match market rates."
        elif current_price > avg_price * 1.2:
            return f"Your price is above the average ({avg_price:.0f} ETB) for similar products. Consider reducing to stay competitive."
        else:
            return f"Your price is within the typical range ({min_price:.0f} - {max_price:.0f} ETB) for similar products."
    
    def record_transaction(self, product_name, price, action):
        """Record a buy/sell transaction"""
        if 'transactions' not in self.__dict__:
            self.transaction_data = []
        
        self.transaction_data.append({
            'product_name': product_name,
            'total_amount': price,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
        # Save to database if needed
        self.save_transactions()
    
    def save_transactions(self):
        """Save transactions to file"""
        try:
            with open(f"{self.data_dir}/transactions_{self.user_id}.json", 'w') as f:
                json.dump(self.transaction_data, f, indent=2)
        except Exception as e:
            pass
    
    def get_demand_analysis(self):
        """Get demand analysis based on user's transactions"""
        product_demand = defaultdict(int)
        product_transactions = defaultdict(list)
        
        for trans in self.transaction_data:
            product_name = trans.get('product_name', '')
            if product_name:
                product_demand[product_name] += 1
                product_transactions[product_name].append(trans)
        
        # Get recent transactions (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_products = defaultdict(int)
        
        for trans in self.transaction_data:
            try:
                trans_date = datetime.fromisoformat(trans.get('timestamp', datetime.now().isoformat()))
                if trans_date > week_ago:
                    product_name = trans.get('product_name', '')
                    if product_name:
                        recent_products[product_name] += 1
            except:
                pass
        
        # Determine demand levels
        demand_levels = {}
        all_products = set(product_demand.keys()) | set(recent_products.keys())
        
        for product in all_products:
            total_count = product_demand.get(product, 0)
            recent_count = recent_products.get(product, 0)
            
            if total_count > 10:
                demand_levels[product] = '🔥 High Demand'
            elif total_count > 5:
                demand_levels[product] = '📈 Growing Demand'
            elif total_count > 0:
                demand_levels[product] = '📊 Moderate Demand'
            else:
                demand_levels[product] = '📉 Low Demand'
        
        return {
            'demand_levels': demand_levels,
            'total_transactions': len(self.transaction_data),
            'unique_products': len(product_demand),
            'recent_activity': len(recent_products)
        }


# ==========================================
# RECOMMENDATION SYSTEM
# ==========================================

class RecommendationSystem:
    """Product recommendation system based on user behavior"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_products = []
        self.user_orders = []
        self.view_history = []
        self.load_user_data()
        
    def load_user_data(self):
        """Load user data from database"""
        try:
            products = get_products(producer_id=self.user_id)
            self.user_products = products if products else []
            
            orders = get_orders(self.user_id, 'producer', limit=50)
            self.user_orders = orders if orders else []
            
            view_path = f"data/view_history_{self.user_id}.json"
            if os.path.exists(view_path):
                with open(view_path, 'r') as f:
                    self.view_history = json.load(f)
            else:
                self.view_history = []
                
        except Exception as e:
            self.user_products = []
            self.user_orders = []
            self.view_history = []
    
    def save_view_history(self):
        """Save view history"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(f"data/view_history_{self.user_id}.json", 'w') as f:
                json.dump(self.view_history, f, indent=2)
        except Exception as e:
            pass
    
    def add_view(self, product_name):
        """Add product to view history"""
        entry = {
            'product': product_name,
            'timestamp': datetime.now().isoformat()
        }
        self.view_history.append(entry)
        
        if len(self.view_history) > 100:
            self.view_history = self.view_history[-100:]
        
        self.save_view_history()
    
    def get_user_behavior_summary(self):
        """Get summary of user behavior"""
        behavior = {
            'products': [p.get('name') for p in self.user_products if p.get('name')],
            'transactions': [o.get('product_name') for o in self.user_orders if o.get('product_name')],
            'categories': [],
            'avg_price': 0,
            'viewed_products': [v.get('product') for v in self.view_history if v.get('product')]
        }
        
        # Get categories
        categories = set()
        prices = []
        for product in self.user_products:
            if product.get('category'):
                categories.add(product.get('category'))
            if product.get('price', 0) > 0:
                prices.append(product.get('price', 0))
        
        behavior['categories'] = list(categories)
        behavior['avg_price'] = sum(prices) / len(prices) if prices else 0
        
        return behavior
    
    def get_recommendations(self, product_name, market_data):
        """Get product recommendations based on user behavior and market data"""
        # Get user behavior summary
        behavior = self.get_user_behavior_summary()
        
        # Query Groq for recommendations
        result = query_groq_recommendations(product_name, behavior, market_data)
        
        if result.get('success') and result.get('recommendations'):
            return result.get('recommendations', [])
        else:
            return self.get_fallback_recommendations(product_name)
    
    def get_fallback_recommendations(self, product_name):
        """Get fallback recommendations"""
        recommendations = []
        
        # Get user's product categories
        user_categories = set()
        for product in self.user_products:
            user_categories.add(product.get('category', 'Other'))
        
        # Category-based product suggestions
        category_products = {
            'Grains': ['Teff', 'Wheat', 'Barley', 'Maize', 'Sorghum'],
            'Vegetables': ['Onion', 'Tomato', 'Cabbage', 'Potato', 'Carrot'],
            'Fruits': ['Banana', 'Mango', 'Avocado', 'Orange', 'Papaya'],
            'Dairy': ['Milk', 'Butter', 'Cheese', 'Yogurt'],
            'Meat': ['Beef', 'Chicken', 'Mutton', 'Goat'],
            'Coffee': ['Coffee'],
            'Other': ['Honey', 'Sesame', 'Sugar', 'Oil']
        }
        
        # Get products from user's categories
        for category in user_categories:
            if category in category_products:
                for prod in category_products[category][:2]:
                    if prod != product_name and not any(r['name'] == prod for r in recommendations):
                        recommendations.append({
                            'name': prod,
                            'reason': f'Similar to your {category.lower()} products',
                            'price_min': None,
                            'price_max': None
                        })
        
        return recommendations[:5]


# ==========================================
# RENDER AI INSIGHTS TAB
# ==========================================

def render_ai_insights(user_info, ai=None):
    """Render AI Insights tab with Price Prediction & Recommendation System"""
    
    # Initialize systems
    price_predictor = PricePredictionSystem(user_info['id'])
    recommender = RecommendationSystem(user_info['id'])
    
    st.markdown("""
    <style>
    .search-bar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #0a0e1a;
        padding: 12px 16px;
        border-bottom: 1px solid #2d3748;
        margin-bottom: 16px;
        border-radius: 12px;
    }
    .search-bar input {
        width: 100%;
        padding: 10px 18px;
        border-radius: 25px;
        border: 1px solid #2d3748;
        background: #1a1a2e;
        color: #f8fafc;
        font-size: 14px;
        outline: none;
    }
    .search-bar input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    .search-bar input::placeholder {
        color: #64748b;
    }
    .result-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .result-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .result-card .title {
        color: #f8fafc;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .result-card .subtitle {
        color: #94a3b8;
        font-size: 13px;
        margin-bottom: 8px;
    }
    .result-card .price {
        color: #10b981;
        font-size: 24px;
        font-weight: 700;
    }
    .badge-fair-yes {
        background: #10b981;
        color: white;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-fair-no {
        background: #ef4444;
        color: white;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-fair-maybe {
        background: #f59e0b;
        color: white;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .rec-card {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #2d3748;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .rec-card:hover {
        border-color: #667eea;
        transform: translateX(4px);
    }
    .rec-card .name {
        color: #f8fafc;
        font-weight: 500;
    }
    .rec-card .reason {
        color: #94a3b8;
        font-size: 12px;
    }
    .rec-card .price {
        color: #10b981;
        font-weight: 600;
        font-size: 14px;
    }
    .demand-card {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid #2d3748;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .demand-card:hover {
        border-color: #f59e0b;
    }
    .demand-card .name {
        color: #f8fafc;
        font-weight: 500;
    }
    .demand-card .level {
        font-weight: 600;
        font-size: 14px;
    }
    .demand-high { color: #10b981; }
    .demand-growing { color: #f59e0b; }
    .demand-moderate { color: #3b82f6; }
    .demand-low { color: #ef4444; }
    .light-mode .search-bar {
        background: #f8fafc;
        border-bottom-color: #e2e8f0;
    }
    .light-mode .search-bar input {
        background: #ffffff;
        color: #1e293b;
        border-color: #e2e8f0;
    }
    .light-mode .result-card {
        background: #ffffff;
        border-color: #e2e8f0;
    }
    .light-mode .result-card .title {
        color: #0f172a;
    }
    .light-mode .rec-card {
        background: #ffffff;
        border-color: #e2e8f0;
    }
    .light-mode .rec-card .name {
        color: #0f172a;
    }
    .light-mode .demand-card {
        background: #ffffff;
        border-color: #e2e8f0;
    }
    .light-mode .demand-card .name {
        color: #0f172a;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # FLOATING SEARCH BAR
    # ==========================================
    search_query = st.text_input(
        "🔍 Search Products",
        placeholder="Type product name...",
        key="search_input",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # ==========================================
    # TAB LAYOUT
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📊 Price Prediction", "🎯 Recommendations", "📈 Demand Analysis"])
    
    # ==========================================
    # TAB 1: PRICE PREDICTION
    # ==========================================
    with tab1:
        st.subheader("📊 Price Prediction System")
        st.caption("Get price predictions based on your posted products and transaction history")
        
        user_products = get_products(producer_id=user_info['id'])
        
        if not user_products:
            st.warning("⚠️ No products found. Please add products in the Inventory tab first.")
            
            # Show sample prediction
            st.info("💡 Sample Prediction (based on user data):")
            sample_data = {
                'product_name': 'Sample Product',
                'current_price': 100,
                'prediction': {
                    'is_fair': 'Yes',
                    'ideal_min': 90,
                    'ideal_max': 110,
                    'recommendation': 'Maintain',
                    'confidence': 'MEDIUM',
                    'explanation': 'Based on your product data and transaction history.',
                    'data_points': 8
                }
            }
            display_prediction(sample_data)
            return
        
        # Product selection
        product_options = [p['name'] for p in user_products]
        selected_product = st.selectbox(
            "Select a product to predict",
            product_options,
            help="Choose a product from your inventory"
        )
        
        # Search filter for products
        if search_query:
            filtered_options = [p for p in product_options if search_query.lower() in p.lower()]
            if filtered_options:
                selected_product = filtered_options[0]
        
        # Get product details
        product_data = next((p for p in user_products if p['name'] == selected_product), None)
        
        if product_data:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Product:** {product_data.get('name', 'Unknown')}")
                st.markdown(f"**Category:** {product_data.get('category', 'N/A')}")
                st.markdown(f"**Current Price:** {product_data.get('price', 0)} ETB")
                st.markdown(f"**Data Points:** {len([p for p in user_products if p.get('category') == product_data.get('category')])} similar products")
            with col2:
                if st.button("🔮 Predict Price", use_container_width=True, type="primary"):
                    with st.spinner(f"Analyzing {selected_product}..."):
                        result = price_predictor.predict_price(
                            selected_product,
                            product_data.get('price', 0)
                        )
                        st.session_state.prediction_result = result
                        st.rerun()
            
            # Display prediction result
            if 'prediction_result' in st.session_state:
                display_prediction({
                    'product_name': selected_product,
                    'current_price': product_data.get('price', 0),
                    'prediction': st.session_state.prediction_result
                })
        
        # Show prediction history
        if price_predictor.prediction_history:
            with st.expander("📋 Prediction History", expanded=False):
                for pred in price_predictor.prediction_history[-5:]:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="title">{pred['product']}</div>
                        <div class="subtitle">
                            Price: {pred['current_price']} ETB | 
                            Fair: {pred['prediction'].get('is_fair', 'N/A')} | 
                            Confidence: {pred['prediction'].get('confidence', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ==========================================
    # TAB 2: RECOMMENDATIONS
    # ==========================================
    with tab2:
        st.subheader("🎯 Product Recommendations")
        st.caption("AI-powered recommendations based on your behavior and market trends")
        
        # User behavior summary
        behavior = recommender.get_user_behavior_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Products Posted", len(behavior.get('products', [])))
        with col2:
            st.metric("📋 Orders", len(behavior.get('transactions', [])))
        with col3:
            st.metric("👁️ Viewed", len(behavior.get('viewed_products', [])))
        with col4:
            st.metric("💰 Avg Price", f"{behavior.get('avg_price', 0):.0f} ETB")
        
        st.markdown("---")
        
        # Get market data from user's own products
        market_data = {
            'popular': behavior.get('products', [])[:5],
            'trending': behavior.get('viewed_products', [])[:5],
            'high_demand': [p for p in behavior.get('products', []) if p]  # From user's own products
        }
        
        # Get recommendations
        if st.button("🔄 Get Personalized Recommendations", use_container_width=True, type="primary"):
            with st.spinner("Analyzing your behavior and generating recommendations..."):
                if user_products:
                    base_product = user_products[0]['name']
                    recommendations = recommender.get_recommendations(base_product, market_data)
                    st.session_state.recommendations = recommendations
                    st.rerun()
                else:
                    st.warning("Please add products first to get personalized recommendations.")
        
        # Display recommendations
        if 'recommendations' in st.session_state and st.session_state.recommendations:
            st.markdown("#### 📌 Recommended Products")
            
            for i, rec in enumerate(st.session_state.recommendations, 1):
                price_display = f"{rec.get('price_min', 0):.0f} - {rec.get('price_max', 0):.0f} ETB" if rec.get('price_min') else "Price varies"
                st.markdown(f"""
                <div class="rec-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="name">{i}. {rec.get('name', 'Unknown')}</span>
                            <div class="reason">{rec.get('reason', 'Recommended based on your behavior')}</div>
                        </div>
                        <div class="price">
                            {price_display}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Click 'Get Personalized Recommendations' to see products tailored to your behavior.")
        
        # Popular products from user's data
        st.markdown("---")
        st.markdown("#### 📦 Products from Your Inventory")
        
        if user_products:
            for product in user_products[:6]:
                st.markdown(f"""
                <div class="rec-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="name">{product.get('name', 'Unknown')}</span>
                            <div class="reason">Category: {product.get('category', 'Other')}</div>
                        </div>
                        <div class="price">{product.get('price', 0)} ETB</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No products in your inventory yet.")
    
    # ==========================================
    # TAB 3: DEMAND ANALYSIS
    # ==========================================
    with tab3:
        st.subheader("📈 Demand Analysis")
        st.caption("Demand analysis based on your transactions and product activity")
        
        # Get demand analysis
        demand_analysis = price_predictor.get_demand_analysis()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Transactions", demand_analysis.get('total_transactions', 0))
        with col2:
            st.metric("📦 Unique Products", demand_analysis.get('unique_products', 0))
        with col3:
            st.metric("📈 Recent Activity", demand_analysis.get('recent_activity', 0))
        
        st.markdown("---")
        
        # Demand levels
        demand_levels = demand_analysis.get('demand_levels', {})
        
        if demand_levels:
            st.markdown("#### 📊 Product Demand Levels (Based on Your Transactions)")
            
            # Sort by demand level
            sorted_products = sorted(
                demand_levels.items(),
                key=lambda x: (
                    0 if 'High' in x[1] else 1 if 'Growing' in x[1] else 2 if 'Moderate' in x[1] else 3
                )
            )
            
            for product, level in sorted_products:
                if 'High' in level:
                    level_class = "demand-high"
                elif 'Growing' in level:
                    level_class = "demand-growing"
                elif 'Moderate' in level:
                    level_class = "demand-moderate"
                else:
                    level_class = "demand-low"
                
                st.markdown(f"""
                <div class="demand-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="name">{product}</span>
                        <span class="level {level_class}">{level}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No demand data available. Start adding transactions to see demand analysis.")
        
        st.markdown("---")
        st.markdown("#### 💡 How Demand is Calculated")
        st.caption("""
        - **High Demand**: More than 10 transactions
        - **Growing Demand**: 5-10 transactions
        - **Moderate Demand**: 1-5 transactions
        - **Low Demand**: No recent activity
        """)
        
        # Add transaction button
        st.markdown("---")
        st.markdown("#### ➕ Record Transaction")
        st.caption("Add a transaction to improve demand analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            product_name = st.text_input("Product Name", placeholder="e.g., Teff, Coffee")
        with col2:
            price = st.number_input("Price (ETB)", min_value=0.0, step=1.0)
        with col3:
            action = st.selectbox("Action", ["buy", "sell"])
        
        if st.button("💾 Record Transaction", use_container_width=True):
            if product_name and price > 0:
                price_predictor.record_transaction(product_name, price, action)
                st.success(f"✅ Transaction recorded for {product_name}")
                st.rerun()
            else:
                st.error("❌ Please fill in all fields")


def display_prediction(data):
    """Display prediction results in a card"""
    product_name = data.get('product_name', 'Unknown')
    current_price = data.get('current_price', 0)
    prediction = data.get('prediction', {})
    
    is_fair = prediction.get('is_fair', 'Unknown')
    ideal_min = prediction.get('ideal_min')
    ideal_max = prediction.get('ideal_max')
    recommendation = prediction.get('recommendation', 'N/A')
    confidence = prediction.get('confidence', 'LOW')
    explanation = prediction.get('explanation', '')
    data_points = prediction.get('data_points', 0)
    
    # Fair badge
    if is_fair == "Yes":
        badge_class = "badge-fair-yes"
    elif is_fair == "No (Too Low)" or is_fair == "No (Too High)":
        badge_class = "badge-fair-no"
    else:
        badge_class = "badge-fair-maybe"
    
    st.markdown(f"""
    <div class="result-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div class="title">{product_name}</div>
                <div class="subtitle">
                    Current Price: {current_price:.0f} ETB | 
                    <span class="{badge_class}">Fair Price: {is_fair}</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="color: #94a3b8; font-size: 12px;">Recommendation</div>
                <div style="color: {'#10b981' if recommendation == 'Maintain' else '#f59e0b' if recommendation == 'Increase' else '#ef4444' if recommendation == 'Decrease' else '#94a3b8'}; font-weight: 600; font-size: 16px;">
                    {recommendation}
                </div>
            </div>
        </div>
        
        <div style="display: flex; gap: 20px; margin: 12px 0; flex-wrap: wrap;">
            <div>
                <span style="color: #94a3b8; font-size: 12px;">Ideal Range</span>
                <div style="color: #f8fafc; font-weight: 600;">
                    {f'{ideal_min:.0f} - {ideal_max:.0f} ETB' if ideal_min and ideal_max else 'Insufficient data'}
                </div>
            </div>
            <div>
                <span style="color: #94a3b8; font-size: 12px;">Confidence</span>
                <div style="color: {'#10b981' if confidence == 'HIGH' else '#f59e0b' if confidence == 'MEDIUM' else '#ef4444'}; font-weight: 600;">
                    {confidence}
                </div>
            </div>
            <div>
                <span style="color: #94a3b8; font-size: 12px;">Data Points</span>
                <div style="color: #f8fafc; font-weight: 600;">
                    {data_points}
                </div>
            </div>
        </div>
        
        <div style="color: #94a3b8; font-size: 13px; margin-top: 8px; padding-top: 8px; border-top: 1px solid #1e293b;">
            💡 {explanation}
        </div>
    </div>
    """, unsafe_allow_html=True)
