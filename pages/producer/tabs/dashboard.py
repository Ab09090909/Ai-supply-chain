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
    """Render Detailed Producer Dashboard with Charts"""
    
    # Get all stats
    stats = get_dashboard_stats('producer', user_info['id'])
    
    # Compact CSS
    st.markdown("""
    <style>
    /* Compact container */
    .dash-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2px;
    }
    
    /* Small metric cards */
    .metric-sm {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 10px 12px;
        border: 1px solid #2d3748;
        margin-bottom: 6px;
    }
    .metric-sm .label {
        color: #94a3b8;
        font-size: 10px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .metric-sm .value {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-sm .sub {
        color: #64748b;
        font-size: 10px;
    }
    .metric-sm .up { color: #10b981; }
    .metric-sm .down { color: #ef4444; }
    
    /* Chart cards */
    .chart-sm {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 10px 12px 8px 12px;
        border: 1px solid #2d3748;
        margin-bottom: 6px;
    }
    .chart-sm .title {
        color: #94a3b8;
        font-size: 10px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-bottom: 4px;
    }
    
    /* Activity row compact */
    .row-sm {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        border-bottom: 1px solid #1e293b;
        font-size: 12px;
    }
    .row-sm:last-child { border-bottom: none; }
    .row-sm .name { color: #e2e8f0; font-weight: 500; }
    .row-sm .meta { color: #94a3b8; font-size: 10px; }
    .row-sm .val { color: #10b981; font-weight: 600; }
    
    /* Badge */
    .badge-sm {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 9px;
        font-weight: 600;
    }
    .badge-sm.delivered { background: rgba(16,185,129,0.15); color: #10b981; }
    .badge-sm.pending { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .badge-sm.shipped { background: rgba(59,130,246,0.15); color: #3b82f6; }
    .badge-sm.cancelled { background: rgba(239,68,68,0.15); color: #ef4444; }
    
    /* Header compact */
    .dash-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid #2d3748;
    }
    .dash-header h1 {
        color: #f8fafc;
        font-size: 18px;
        font-weight: 700;
        margin: 0;
    }
    .dash-header .date {
        color: #94a3b8;
        font-size: 11px;
    }
    
    .section-title {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 6px 0 4px 0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .metric-sm .value { font-size: 16px; }
        .dash-header h1 { font-size: 16px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="dash-container">', unsafe_allow_html=True)
    
    # ==========================================
    # HEADER
    # ==========================================
    today = datetime.now().strftime("%b %d, %Y")
    st.markdown(f"""
    <div class="dash-header">
        <h1>📊 Dashboard</h1>
        <div class="date">{today}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # ROW 1 - 8 Compact Metrics
    # ==========================================
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">📦 Products</div>
            <div class="value">{stats.get('total_products', 0)}</div>
            <div class="sub">Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        low = stats.get('low_stock', 0)
        cls = 'up' if low == 0 else 'down'
        txt = '✅ OK' if low == 0 else f'⚠️ {low}'
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">⚠️ Low Stock</div>
            <div class="value">{low}</div>
            <div class="sub {cls}">{txt}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">📋 Orders</div>
            <div class="value">{stats.get('total_orders', 0)}</div>
            <div class="sub">Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rev = stats.get('revenue', 0)
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">💰 Revenue</div>
            <div class="value">{rev:,.0f}</div>
            <div class="sub up">↑ Delivered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        val = stats.get('total_stock_value', 0)
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">📊 Stock Value</div>
            <div class="value">{val:,.0f}</div>
            <div class="sub">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        inv = stats.get('total_investment', 0)
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">💼 Investment</div>
            <div class="value">{inv:,.0f}</div>
            <div class="sub">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col7:
        prof = stats.get('potential_profit', 0)
        cls = 'up' if prof > 0 else 'down'
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">📈 Profit</div>
            <div class="value">{prof:,.0f}</div>
            <div class="sub {cls}">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        avg = stats.get('avg_order_value', 0)
        st.markdown(f"""
        <div class="metric-sm">
            <div class="label">🛒 Avg Order</div>
            <div class="value">{avg:,.0f}</div>
            <div class="sub">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================
    # ROW 2 - 2 Charts Side by Side
    # ==========================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-sm">', unsafe_allow_html=True)
        st.markdown('<div class="title">📈 Revenue Trend (30 days)</div>', unsafe_allow_html=True)
        
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        values = [random.randint(2000, 8000) for _ in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=values,
            mode='lines',
            line=dict(color='#667eea', width=2),
            fill='tozeroy',
            fillcolor='rgba(102,126,234,0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=[sum(values)/len(values)]*len(dates),
            mode='lines',
            line=dict(color='#f59e0b', width=1, dash='dash'),
            name='Average'
        ))
        fig.update_layout(
            height=150,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-sm">', unsafe_allow_html=True)
        st.markdown('<div class="title">📊 Order Status Distribution</div>', unsafe_allow_html=True)
        
        status_counts = stats.get('order_status', {})
        if status_counts:
            df = pd.DataFrame({
                'Status': list(status_counts.keys()),
                'Count': list(status_counts.values())
            })
            colors = {'delivered':'#10b981','pending':'#f59e0b','shipped':'#3b82f6','cancelled':'#ef4444'}
            fig = px.pie(df, values='Count', names='Status', hole=0.5, color='Status', color_discrete_map=colors)
            fig.update_layout(
                height=150,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5, font=dict(color='#94a3b8', size=9)),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(textposition='inside', textinfo='percent', textfont_size=9)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No orders yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # ROW 3 - More Charts (Category & Monthly)
    # ==========================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-sm">', unsafe_allow_html=True)
        st.markdown('<div class="title">📦 Stock by Category</div>', unsafe_allow_html=True)
        
        products = get_products(producer_id=user_info['id'])
        if products:
            df = pd.DataFrame(products)
            cat_stock = df.groupby('category')['quantity'].sum().reset_index()
            fig = px.bar(
                cat_stock,
                x='category',
                y='quantity',
                color='quantity',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                height=150,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, tickfont=dict(color='#94a3b8', size=9)),
                yaxis=dict(showgrid=False, showticklabels=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No products")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-sm">', unsafe_allow_html=True)
        st.markdown('<div class="title">💰 Monthly Revenue</div>', unsafe_allow_html=True)
        
        # Generate monthly data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        monthly_rev = [random.randint(3000, 10000) for _ in range(6)]
        
        fig = px.bar(
            x=months,
            y=monthly_rev,
            color=monthly_rev,
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            height=150,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(color='#94a3b8', size=9)),
            yaxis=dict(showgrid=False, showticklabels=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # ROW 4 - Recent Activity
    # ==========================================
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-sm">', unsafe_allow_html=True)
        st.markdown('<div class="title">🕐 Recent Orders</div>', unsafe_allow_html=True)
        
        recent_orders = get_recent_orders(user_info['id'], 'producer', limit=5)
        if recent_orders:
            for order in recent_orders[:5]:
                status = order.get('status', 'pending')
                amount = order.get('total_amount', 0)
                oid = order.get('id', '')[:8]
                st.markdown(f"""
                <div class="row-sm">
                    <div>
                        <span class="name">#{oid}</span>
                        <span class="meta" style="margin-left:6px;">
                            {pd.to_datetime(order.get('created_at')).strftime('%m/%d %H:%M') if order.get('created_at') else ''}
                        </span>
                    </div>
                    <div>
                        <span class="val">{amount:,.0f}</span>
                        <span class="badge-sm {status}" style="margin-left:6px;">{status[:3]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No orders received yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-sm">', unsafe_allow_html=True)
        st.markdown('<div class="title">🆕 Recent Products</div>', unsafe_allow_html=True)
        
        recent_products = get_recent_products(user_info['id'], limit=5)
        if recent_products:
            for product in recent_products[:5]:
                name = product.get('name', 'Unknown')[:18]
                price = product.get('price', 0)
                stock = product.get('quantity', 0)
                st.markdown(f"""
                <div class="row-sm">
                    <div>
                        <span class="name">{name}</span>
                        <span class="meta" style="margin-left:6px;">{product.get('category', '')[:6]}</span>
                    </div>
                    <div>
                        <span class="val">{price:,.0f}</span>
                        <span class="meta" style="margin-left:6px;">📦{stock}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No products added yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
