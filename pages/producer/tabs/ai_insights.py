# pages/producer/tabs/ai_insights_enhanced.py
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
# WORLD BANK API INTEGRATION
# ==========================================

def fetch_world_bank_data(commodity_code="PMAIZMT", start_year=2015, end_year=2026):
    """Fetch commodity price data from World Bank API"""
    try:
        url = f"https://api.worldbank.org/v2/country/all/indicator/{commodity_code}?format=json&date={start_year}:{end_year}&per_page=100"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and 'value' in data[1][0]:
                prices = []
                for item in data[1]:
                    if item.get('value'):
                        prices.append({
                            'date': item.get('date'),
                            'value': float(item.get('value'))
                        })
                return prices
        return None
    except Exception as e:
        return None

# Commodity codes mapping for Ethiopian commodities
COMMODITY_CODES = {
    'Teff': 'PMAIZMT',  # Maize price (closest match)
    'Wheat': 'PWHEAMT',
    'Coffee': 'PCOFFOTM',
    'Maize': 'PMAIZMT',
    'Soybean': 'PSOYBM',
    'Rice': 'PRICENP',
    'Sugar': 'PSUGARB',
    'Cotton': 'PCOTTON'
}

# ==========================================
# GROQ API FOR PREDICTION
# ==========================================

def get_groq_api_key():
    """Get Groq API key from secrets"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("groq_api_key") or st.secrets.get("GROQ_KEY")
        return api_key
    except Exception as e:
        return None

def query_groq_prediction(product_name, region="Addis Ababa", historical_prices=None):
    """Query Groq API for market predictions"""
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
        
        # Build context with historical data if available
        historical_context = ""
        if historical_prices:
            recent_prices = historical_prices[-12:]  # Last 12 months
            historical_context = f"""
Historical price data (last 12 months):
{json.dumps(recent_prices, indent=2)}
"""
        
        prompt = f"""Analyze the Ethiopian {product_name} market in {region} and provide:

1. Current estimated price in ETB per kg
2. Price prediction for the next 30 days
3. Price prediction for the next 6 months
4. Key market factors affecting prices
5. Recommended price strategy

{historical_context}

Please provide a detailed analysis with specific numbers and actionable insights."""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": """You are a commodity market analyst specializing in Ethiopian agricultural products. 
                You provide accurate price predictions and market analysis based on historical trends and current conditions.
                Always give specific price numbers in ETB per kg."""},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.1
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
            current_match = re.search(r'Current.*?(?:price|estimate):?\s*([\d.]+)', content, re.IGNORECASE)
            thirty_day_match = re.search(r'30\s*day.*?(?:price|prediction|forecast):?\s*([\d.]+)', content, re.IGNORECASE)
            six_month_match = re.search(r'6\s*month.*?(?:price|prediction|forecast):?\s*([\d.]+)', content, re.IGNORECASE)
            
            result = {
                "success": True,
                "raw_response": content,
                "source": "Groq API"
            }
            
            if current_match:
                result["current_price"] = float(current_match.group(1))
            if thirty_day_match:
                result["prediction_30d"] = float(thirty_day_match.group(1))
            if six_month_match:
                result["prediction_6m"] = float(six_month_match.group(1))
            
            return result
        else:
            return {
                "success": False,
                "error": "Unexpected API response"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# ETHIOPIAN MARKET PRICE DATABASE
# ==========================================

def get_ethiopian_market_price(product_name):
    """Get current Ethiopian market prices"""
    
    ethiopian_prices = {
        'teff': {'price': 120, 'min': 110, 'max': 130, 'trend': 'increasing', 'demand': 'high'},
        'wheat': {'price': 65, 'min': 55, 'max': 75, 'trend': 'stable', 'demand': 'high'},
        'coffee': {'price': 340, 'min': 280, 'max': 400, 'trend': 'increasing', 'demand': 'high'},
        'milk': {'price': 75, 'min': 60, 'max': 90, 'trend': 'increasing', 'demand': 'high'},
        'beef': {'price': 520, 'min': 450, 'max': 600, 'trend': 'increasing', 'demand': 'high'},
        'onion': {'price': 40, 'min': 30, 'max': 50, 'trend': 'volatile', 'demand': 'high'},
        'tomato': {'price': 45, 'min': 35, 'max': 60, 'trend': 'volatile', 'demand': 'high'},
        'potato': {'price': 50, 'min': 40, 'max': 65, 'trend': 'increasing', 'demand': 'medium'},
        'barley': {'price': 45, 'min': 35, 'max': 55, 'trend': 'stable', 'demand': 'medium'},
        'maize': {'price': 40, 'min': 30, 'max': 55, 'trend': 'stable', 'demand': 'medium'},
    }
    
    product_key = product_name.lower().strip()
    for key in ethiopian_prices:
        if product_key in key or key in product_key:
            return ethiopian_prices[key]
    
    return {'price': 125, 'min': 80, 'max': 200, 'trend': 'stable', 'demand': 'medium'}

# ==========================================
# RENDER AI INSIGHTS ENHANCED TAB
# ==========================================

def render_ai_insights_enhanced(user_info):
    """Render enhanced AI Insights tab with World Bank + Groq"""
    
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
    .badge-groq {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .badge-worldbank {
        display: inline-block;
        background: #f59e0b;
        color: #0f172a;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .badge-estimate {
        display: inline-block;
        background: #64748b;
        color: white;
        font-size: 10px;
        padding: 2px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("🚀 Enhanced AI Market Insights")
    st.caption("Powered by World Bank Data + Groq AI Predictions")
    
    # API Key Check
    api_key = get_groq_api_key()
    if not api_key:
        st.warning("⚠️ Groq API key not found. Please add GROQ_API_KEY to secrets for AI predictions.")
        st.info("Format: GROQ_API_KEY = 'your_key_here'")
    
    # Get products
    all_products = get_products(producer_id=user_info['id'])
    user_product_names = [p['name'] for p in all_products] if all_products else []
    
    # Product selection
    st.markdown("### 🔍 Select Commodity")
    
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
    
    # Fetch World Bank data
    with st.spinner(f"Fetching global data for {product_name}..."):
        commodity_code = COMMODITY_CODES.get(product_name, "PMAIZMT")
        world_bank_data = fetch_world_bank_data(commodity_code)
    
    # Get Ethiopian market data
    ethiopian_data = get_ethiopian_market_price(product_name)
    
    # Get Groq prediction
    st.markdown("### 🤖 AI Price Prediction")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Analyzing {product_name} market in {selected_region} with World Bank + Groq AI")
    with col2:
        if st.button("🔮 Predict Now", use_container_width=True, type="primary"):
            with st.spinner(f"Analyzing {product_name} with AI..."):
                groq_result = query_groq_prediction(product_name, selected_region, world_bank_data)
                st.session_state.groq_prediction = groq_result
                if groq_result.get('success'):
                    st.success("✅ Prediction complete!")
                    st.rerun()
                else:
                    st.error(f"❌ {groq_result.get('error', 'Prediction failed')}")
    
    # Display results
    st.markdown("### 📊 Market Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">📈 Current Market Price</div>
            <div class="value">{ethiopian_data.get('price', 125)} ETB/kg</div>
            <div class="sub">Range: {ethiopian_data.get('min', 80)} - {ethiopian_data.get('max', 200)} ETB</div>
            <div class="sub">Trend: <span class="trend-{ethiopian_data.get('trend', 'stable')}">{ethiopian_data.get('trend', 'stable').capitalize()}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        groq_pred = st.session_state.get('groq_prediction', {})
        if groq_pred.get('success'):
            st.markdown(f"""
            <div class="prediction-card">
                <div class="label">🤖 AI Predicted Price (30 Days)</div>
                <div class="price">{groq_pred.get('prediction_30d', 'N/A')} ETB/kg</div>
                <div class="sub">Current: {groq_pred.get('current_price', 'N/A')} ETB</div>
                <span class="badge-groq">Groq AI</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="prediction-card">
                <div class="label">📊 6-Month Forecast</div>
                <div class="price">-</div>
                <div class="sub">Click "Predict Now" for AI analysis</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if groq_pred.get('success'):
            st.markdown(f"""
            <div class="prediction-card">
                <div class="label">📊 6-Month Forecast</div>
                <div class="price">{groq_pred.get('prediction_6m', 'N/A')} ETB/kg</div>
                <div class="sub">Change: {((groq_pred.get('prediction_6m', 0) - groq_pred.get('current_price', 0)) / groq_pred.get('current_price', 1) * 100):+.1f}%</div>
                <span class="badge-groq">AI Prediction</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="prediction-card">
                <div class="label">🔮 Market Sentiment</div>
                <div class="price" style="font-size:20px;">Waiting for prediction</div>
                <div class="sub">Click "Predict Now" for analysis</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # World Bank Data
    st.markdown("### 🌍 World Bank Historical Data")
    
    if world_bank_data:
        st.caption(f"Historical price data for {product_name} (World Bank)")
        
        # Create chart
        df = pd.DataFrame(world_bank_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        st.line_chart(df.set_index('date')['value'], height=200)
        
        # Show recent data
        st.caption(f"Latest World Bank price: {world_bank_data[-1]['value']:.2f} (as of {world_bank_data[-1]['date']})")
    else:
        st.info(f"No World Bank data available for {product_name}. Using Ethiopian market data.")
    
    st.markdown("---")
    
    # AI Analysis
    if groq_pred.get('success'):
        st.markdown("### 🧠 AI Market Analysis")
        st.markdown(f"""
        <div class="insight-card">
            <div class="title">📋 Detailed Analysis</div>
            <div style="color: #e2e8f0; white-space: pre-wrap; font-size: 14px; line-height: 1.6;">
                {groq_pred.get('raw_response', 'No detailed analysis available')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data Sources
    st.caption("📊 Data Sources:")
    st.caption("• Ethiopian Market Data - Local market prices")
    if world_bank_data:
        st.caption("• World Bank API - Global commodity prices")
    if groq_pred.get('success'):
        st.caption("• Groq AI - Market predictions and analysis")
    
    # Save to Supabase
    if groq_pred.get('success'):
        try:
            save_training_data_supabase(user_info['id'], {
                'product_name': product_name,
                'price': ethiopian_data.get('price', 125),
                'market_price': groq_pred.get('current_price', ethiopian_data.get('price', 125)),
                'data_source': 'world_bank_groq',
                'region': selected_region,
                'demand_score': 70,
                'predicted_price': groq_pred.get('prediction_30d', 0)
            })
        except:
            pass
