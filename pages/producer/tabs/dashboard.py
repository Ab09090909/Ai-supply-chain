# pages/producer/tabs/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

from utils.db_helpers import (
    get_products, get_dashboard_stats, get_recent_orders, get_recent_products
)

def render_dashboard(user_info, ai):
    """Render Clean Producer Dashboard"""
    
    # Get all stats
    stats = get_dashboard_stats('producer', user_info['id'])
    
    # Clean CSS
    st.markdown("""
    <style>
    /* Main container */
    .dash-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 4px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 14px 18px;
        border: 1px solid #2d3748;
        margin-bottom: 10px;
    }
    .metric-card .label {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        color: #f8fafc;
        font-size: 26px;
        font-weight: 700;
        line-height: 1.3;
    }
    .metric-card .sub {
        color: #64748b;
        font-size: 12px;
        margin-top: 2px;
    }
    .metric-card .change-up { color: #10b981; }
    .metric-card .change-down { color: #ef4444; }
    .metric-card .change-neutral { color: #f59e0b; }
    
    /* Chart Cards */
    .chart-card {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 14px 16px 10px 16px;
        border: 1px solid #2d3748;
        margin-bottom: 10px;
    }
    .chart-card .title {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    /* Activity Row */
    .activity-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #1e293b;
    }
    .activity-row:last-child {
        border-bottom: none;
    }
    .activity-row .name {
        color: #e2e8f0;
        font-size: 13px;
        font-weight: 500;
    }
    .activity-row .meta {
        color: #94a3b8;
        font-size: 11px;
    }
    .activity-row .amount {
        color: #10b981;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
    }
    .badge.delivered { background: rgba(16,185,129,0.15); color: #10b981; }
    .badge.pending { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .badge.shipped { background: rgba(59,130,246,0.15); color: #3b82f6; }
    .badge.cancelled { background: rgba(239,68,68,0.15); color: #ef4444; }
    
    /* Header */
    .dash-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid #2d3748;
    }
    .dash-header h1 {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 700;
        margin: 0;
    }
    .dash-header .date {
        color: #94a3b8;
        font-size: 13px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .dash-header { flex-direction: column; align-items: flex-start; gap: 6px; }
        .metric-card .value { font-size: 20px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="dash-container">', unsafe_allow_html=True)
    
    # ==========================================
    # HEADER
    # ==========================================
    today = datetime.now().strftime("%B %d, %Y")
    st.markdown(f"""
    <div class="dash-header">
        <h1>📊 Dashboard</h1>
        <div class="date">{today}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # ROW 1 - 4 Key Metrics
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">📦 Products</div>
            <div class="value">{stats.get('total_products', 0)}</div>
            <div class="sub">Active inventory</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        low = stats.get('low_stock', 0)
        cls = 'change-up' if low == 0 else 'change-down'
        txt = '✅ All stocked' if low == 0 else f'⚠️ {low} need restock'
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">⚠️ Low Stock</div>
            <div class="value">{low}</div>
            <div class="sub {cls}">{txt}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">📋 Orders</div>
            <div class="value">{stats.get('total_orders', 0)}</div>
            <div class="sub">Total received</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rev = stats.get('revenue', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">💰 Revenue</div>
            <div class="value">{rev:,.0f} ETB</div>
            <div class="sub change-up">↑ Delivered orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==========================================
    # ROW 2 - 4 Financial Metrics
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        val = stats.get('total_stock_value', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">📊 Stock Value</div>
            <div class="value">{val:,.0f} ETB</div>
            <div class="sub">Current inventory</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        inv = stats.get('total_investment', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">💼 Investment</div>
            <div class="value">{inv:,.0f} ETB</div>
            <div class="sub">Total cost</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        prof = stats.get('potential_profit', 0)
        cls = 'change-up' if prof > 0 else 'change-down'
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">📈 Profit</div>
            <div class="value">{prof:,.0f} ETB</div>
            <div class="sub {cls}">Potential margin</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg = stats.get('avg_order_value', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">🛒 Avg Order</div>
            <div class="value">{avg:,.0f} ETB</div>
            <div class="sub">Per transaction</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==========================================
    # CHARTS ROW
    # ==========================================
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">📈 Revenue Trend</div>', unsafe_allow_html=True)
        
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        values = [random.randint(2000, 8000) for _ in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=values,
            mode='lines',
            line=dict(color='#667eea', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(102,126,234,0.1)'
        ))
        fig.update_layout(
            height=160,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">📊 Order Status</div>', unsafe_allow_html=True)
        
        status_counts = stats.get('order_status', {})
        if status_counts:
            df = pd.DataFrame({
                'Status': list(status_counts.keys()),
                'Count': list(status_counts.values())
            })
            colors = {
                'delivered': '#10b981',
                'pending': '#f59e0b',
                'shipped': '#3b82f6',
                'cancelled': '#ef4444'
            }
            fig = px.pie(
                df, values='Count', names='Status',
                hole=0.5,
                color='Status',
                color_discrete_map=colors
            )
            fig.update_layout(
                height=160,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(textposition='inside', textinfo='percent', textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No orders")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # RECENT ACTIVITY ROW
    # ==========================================
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">🕐 Recent Orders</div>', unsafe_allow_html=True)
        
        recent_orders = get_recent_orders(user_info['id'], 'producer', limit=4)
        if recent_orders:
            for order in recent_orders[:4]:
                status = order.get('status', 'pending')
                amount = order.get('total_amount', 0)
                oid = order.get('id', '')[:8]
                st.markdown(f"""
                <div class="activity-row">
                    <div>
                        <span class="name">#{oid}</span>
                        <span class="meta" style="margin-left:8px;">
                            {pd.to_datetime(order.get('created_at')).strftime('%m/%d %H:%M') if order.get('created_at') else ''}
                        </span>
                    </div>
                    <div>
                        <span class="amount">{amount:,.0f}</span>
                        <span class="badge {status}" style="margin-left:8px;">{status[:3]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No orders received yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">🆕 Recent Products</div>', unsafe_allow_html=True)
        
        recent_products = get_recent_products(user_info['id'], limit=4)
        if recent_products:
            for product in recent_products[:4]:
                name = product.get('name', 'Unknown')[:20]
                price = product.get('price', 0)
                stock = product.get('quantity', 0)
                st.markdown(f"""
                <div class="activity-row">
                    <div>
                        <span class="name">{name}</span>
                        <span class="meta" style="margin-left:8px;">{product.get('category', '')[:8]}</span>
                    </div>
                    <div>
                        <span class="amount">{price:,.0f}</span>
                        <span class="meta" style="margin-left:8px;">📦{stock}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No products added yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
