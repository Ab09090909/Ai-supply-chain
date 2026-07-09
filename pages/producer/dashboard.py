import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_helpers import get_products, get_dashboard_stats

def render_dashboard(user_id):
    """Render producer dashboard"""
    st.subheader("📊 Business Overview")
    
    stats = get_dashboard_stats('producer', user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", stats.get('total_products', 0))
    col2.metric("Low Stock Alerts", stats.get('low_stock', 0), delta_color="inverse")
    col3.metric("Total Orders", stats.get('total_orders', 0))
    col4.metric("Total Revenue", f"{stats.get('revenue', 0):,.2f} ETB")
    
    st.markdown("---")
    
    products = get_products(producer_id=user_id)
    
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
        st.info("📭 No products found. Go to the Inventory tab to add your first product!")
