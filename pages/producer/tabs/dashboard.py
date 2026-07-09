# pages/producer/tabs/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.db_helpers import (
    get_products, get_dashboard_stats, get_recent_orders, get_recent_products
)

def render_dashboard(user_info, ai):
    """Render Complete Dashboard tab"""
    
    # Get all stats
    stats = get_dashboard_stats('producer', user_info['id'])
    
    st.subheader("📊 Business Overview")
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "📦 Total Products", 
            stats.get('total_products', 0),
            help="Total products in your inventory"
        )
    with col2:
        st.metric(
            "⚠️ Low Stock Alerts", 
            stats.get('low_stock', 0),
            delta_color="inverse",
            help="Products below minimum stock level"
        )
    with col3:
        st.metric(
            "📋 Total Orders", 
            stats.get('total_orders', 0),
            help="Total orders received"
        )
    with col4:
        st.metric(
            "💰 Total Revenue", 
            f"{stats.get('revenue', 0):,.2f} ETB",
            delta=f"{stats.get('pending_revenue', 0):,.2f} ETB pending",
            help="Total revenue from delivered orders"
        )
    
    st.markdown("---")
    
    # Additional metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "📊 Stock Value", 
            f"{stats.get('total_stock_value', 0):,.2f} ETB",
            help="Total value of current inventory"
        )
    with col2:
        st.metric(
            "💼 Investment", 
            f"{stats.get('total_investment', 0):,.2f} ETB",
            help="Total cost of inventory"
        )
    with col3:
        st.metric(
            "📈 Potential Profit", 
            f"{stats.get('potential_profit', 0):,.2f} ETB",
            help="Potential profit from current inventory"
        )
    with col4:
        st.metric(
            "📊 Avg Order Value", 
            f"{stats.get('avg_order_value', 0):,.2f} ETB",
            help="Average value per order"
        )
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Order Status Distribution")
        status_counts = stats.get('order_status', {})
        if status_counts:
            # Create pie chart
            df_status = pd.DataFrame({
                'Status': list(status_counts.keys()),
                'Count': list(status_counts.values())
            })
            fig = px.pie(
                df_status, 
                values='Count', 
                names='Status',
                title='Order Status Breakdown',
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4
            )
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=0.95,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No orders to display yet")
    
    with col2:
        st.subheader("📊 Stock by Category")
        products = get_products(producer_id=user_info['id'])
        if products:
            df_products = pd.DataFrame(products)
            category_stock = df_products.groupby('category')['quantity'].sum().reset_index()
            fig = px.bar(
                category_stock,
                x='category',
                y='quantity',
                title='Stock Levels by Category',
                color='quantity',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                xaxis_title="Category",
                yaxis_title="Total Stock"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No products to display")
    
    st.markdown("---")
    
    # Recent Orders and Products
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕐 Recent Orders")
        recent_orders = get_recent_orders(user_info['id'], 'producer', limit=5)
        if recent_orders:
            df_orders = pd.DataFrame(recent_orders)
            display_cols = ['id', 'customer_id', 'total_amount', 'status', 'created_at']
            available_cols = [c for c in display_cols if c in df_orders.columns]
            if available_cols:
                display_df = df_orders[available_cols].copy()
                if 'created_at' in display_df.columns:
                    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
                if 'total_amount' in display_df.columns:
                    display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"{x:.2f} ETB")
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No order data available")
        else:
            st.info("📭 No orders received yet")
    
    with col2:
        st.subheader("🆕 Recent Products")
        recent_products = get_recent_products(user_info['id'], limit=5)
        if recent_products:
            df_products = pd.DataFrame(recent_products)
            display_cols = ['name', 'category', 'price', 'quantity', 'created_at']
            available_cols = [c for c in display_cols if c in df_products.columns]
            if available_cols:
                display_df = df_products[available_cols].copy()
                if 'created_at' in display_df.columns:
                    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
                if 'price' in display_df.columns:
                    display_df['price'] = display_df['price'].apply(lambda x: f"{x:.2f} ETB")
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No product data available")
        else:
            st.info("📭 No products added yet")
    
    st.markdown("---")
    
    # AI Learning Status (collapsible)
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
        
        # Quick Actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Add New Product", use_container_width=True):
                st.session_state.edit_product_id = None
                st.rerun()
        with col2:
            if st.button("📊 View All Products", use_container_width=True):
                st.session_state.active_tab = "Inventory"
                st.rerun()
        with col3:
            if st.button("🤖 AI Insights", use_container_width=True):
                st.session_state.active_tab = "AI Insights"
                st.rerun()
