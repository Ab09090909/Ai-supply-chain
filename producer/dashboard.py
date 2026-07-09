import streamlit as st
from utils.db_helpers import get_dashboard_stats, get_products

def render_dashboard(user_id):
    """Render dashboard tab"""
    st.subheader("📊 Business Overview")
    stats = get_dashboard_stats('producer', user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", stats.get('total_products', 0))
    col2.metric("Low Stock", stats.get('low_stock', 0))
    col3.metric("Total Orders", stats.get('total_orders', 0))
    col4.metric("Revenue", f"{stats.get('revenue', 0):,.0f} ETB")
    
    # You can add charts here...
