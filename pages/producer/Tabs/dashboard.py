import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_helpers import get_products, get_dashboard_stats


def render_dashboard(user_info, ai):
    st.subheader("📊 Business Overview")
    user_id = user_info.get('id')
    stats = get_dashboard_stats('producer', user_id)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", stats.get('total_products', 0))
    col2.metric("Low Stock Alerts", stats.get('low_stock', 0), delta_color="inverse")
    col3.metric("Total Orders", stats.get('total_orders', 0))
    col4.metric("Total Revenue", f"{stats.get('revenue', 0):,.2f} ETB")

    st.markdown("---")
    products = get_products(producer_id=user_id)

    if products:
        df = pd.DataFrame(products)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Stock by Category")
            if 'category' in df.columns and 'quantity' in df.columns:
                fig = px.bar(
                    df.groupby('category')['quantity'].sum().reset_index(),
                    x='category', y='quantity',
                    title="Total Stock per Category",
                    color='quantity', color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Price Distribution")
            if 'price' in df.columns:
                fig2 = px.histogram(
                    df, x='price', nbins=20,
                    title="Product Price Distribution",
                    color_discrete_sequence=['#667eea']
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("🤖 AI Market Tip")
        tip = ai.get_market_tip() if hasattr(ai, 'get_market_tip') else "Keep your stock updated for better demand matching."
        st.info(f"💡 {tip}")
    else:
        st.info("📭 No products yet. Go to the **Inventory** tab to add your first product!")
