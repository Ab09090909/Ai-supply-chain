import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db_helpers import get_products, get_dashboard_stats

def render_dashboard(user_info, ai):
    """Render Dashboard tab"""
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
