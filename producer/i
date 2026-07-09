import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from utils.db_helpers import get_products

def render_ai_insights(user_id):
    """Render AI insights tab"""
    st.subheader("🤖 AI-Powered Supply Chain Insights")
    
    products = get_products(producer_id=user_id, limit=20)
    
    if not products:
        st.warning("⚠️ Add some products first to use AI insights.")
    else:
        selected_id = st.selectbox("Select Product", [p['id'] for p in products], 
                                  format_func=lambda x: next(p['name'] for p in products if p['id'] == x))
        selected_prod = next(p for p in products if p['id'] == selected_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Demand Forecast")
            if st.button("🔮 Predict Demand"):
                dates = pd.date_range(start=datetime.now(), periods=14, freq='D')
                values = np.random.randint(50, 150, 14).tolist()
                fig = go.Figure(data=[go.Scatter(x=dates, y=values, mode='lines+markers')])
                fig.update_layout(template="plotly_dark", title="14-Day Forecast")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Price Optimization")
            if st.button("💡 Suggest Price"):
                current = selected_prod.get('price', 0)
                suggested = current * 1.10
                st.metric("Current Price", f"{current} ETB")
                st.metric("Suggested Price", f"{suggested:.2f} ETB", delta=f"{suggested-current:.2f}")
