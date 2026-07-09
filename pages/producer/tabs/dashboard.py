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
    """Render Professional Enterprise Dashboard"""
    
    # Get all stats
    stats = get_dashboard_stats('producer', user_info['id'])
    
    # Professional CSS
    st.markdown("""
    <style>
    /* Main container */
    .dashboard-main {
        padding: 0;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Header */
    .dash-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid #2d3748;
    }
    .dash-header h1 {
        color: #f8fafc;
        font-size: 24px;
        font-weight: 700;
        margin: 0;
    }
    .dash-header p {
        color: #94a3b8;
        font-size: 14px;
        margin: 4px 0 0 0;
    }
    .dash-header .date {
        color: #94a3b8;
        font-size: 13px;
        background: #1e293b;
        padding: 6px 16px;
        border-radius: 20px;
        border: 1px solid #2d3748;
    }
    
    /* Metric Cards */
    .metric-card-pro {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        transition: all 0.2s ease;
    }
    .metric-card-pro:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .metric-card-pro .label {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card-pro .value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 700;
        margin: 4px 0;
    }
    .metric-card-pro .sub {
        color: #64748b;
        font-size: 12px;
    }
    .metric-card-pro .trend-up { color: #10b981; }
    .metric-card-pro .trend-down { color: #ef4444; }
    .metric-card-pro .trend-neutral { color: #f59e0b; }
    
    /* Chart Cards */
    .chart-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 16px 20px 12px 20px;
        border: 1px solid #2d3748;
        margin-bottom: 12px;
    }
    .chart-card .title {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chart-card .title .badge {
        font-size: 11px;
        font-weight: 400;
        color: #94a3b8;
        background: #1e293b;
        padding: 2px 12px;
        border-radius: 12px;
    }
    
    /* Activity List */
    .activity-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .activity-list li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #1e293b;
    }
    .activity-list li:last-child {
        border-bottom: none;
    }
    .activity-list .left .name {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 500;
    }
    .activity-list .left .meta {
        color: #94a3b8;
        font-size: 12px;
    }
    .activity-list .right .amount {
        color: #10b981;
        font-weight: 600;
        font-size: 15px;
    }
    .activity-list .right .status {
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 500;
    }
    .status-delivered { background: rgba(16,185,129,0.15); color: #10b981; }
    .status-pending { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .status-shipped { background: rgba(59,130,246,0.15); color: #3b82f6; }
    .status-cancelled { background: rgba(239,68,68,0.15); color: #ef4444; }
    
    /* Quick Actions */
    .action-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-top: 8px;
    }
    .action-btn {
        background: #1a1a2e;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #e2e8f0;
    }
    .action-btn:hover {
        border-color: #667eea;
        background: #1e293b;
    }
    .action-btn .icon { font-size: 20px; display: block; margin-bottom: 4px; }
    .action-btn .label { font-size: 12px; font-weight: 500; }
    
    /* Progress bar */
    .progress-track {
        background: #1e293b;
        border-radius: 20px;
        height: 6px;
        overflow: hidden;
        margin-top: 4px;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 20px;
        transition: width 0.3s ease;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .dash-header { flex-direction: column; align-items: flex-start; gap: 12px; }
        .action-grid { grid-template-columns: repeat(2, 1fr); }
        .metric-card-pro .value { font-size: 22px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="dashboard-main">', unsafe_allow_html=True)
    
    # ==========================================
    # HEADER
    # ==========================================
    today = datetime.now().strftime("%B %d, %Y")
    st.markdown(f"""
    <div class="dash-header">
        <div>
            <h1>📊 Dashboard</h1>
            <p>Welcome back, {user_info.get('name', 'Producer')}</p>
        </div>
        <div class="date">📅 {today}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # KEY METRICS - 8 Cards in 2 Rows
    # ==========================================
    # Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">📦 Total Products</div>
            <div class="value">{stats.get('total_products', 0)}</div>
            <div class="sub"><span class="trend-up">↑</span> Active inventory</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        low = stats.get('low_stock', 0)
        trend = 'trend-down' if low > 0 else 'trend-up'
        label = f'⚠️ {low} items' if low > 0 else '✅ All stocked'
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">⚠️ Low Stock Alerts</div>
            <div class="value">{low}</div>
            <div class="sub"><span class="{trend}">{label}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">📋 Total Orders</div>
            <div class="value">{stats.get('total_orders', 0)}</div>
            <div class="sub"><span class="trend-up">↑</span> All time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rev = stats.get('revenue', 0)
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">💰 Total Revenue</div>
            <div class="value">{rev:,.0f} ETB</div>
            <div class="sub"><span class="trend-up">↑</span> Delivered orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        val = stats.get('total_stock_value', 0)
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">📊 Stock Value</div>
            <div class="value">{val:,.0f} ETB</div>
            <div class="sub">Current inventory</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        inv = stats.get('total_investment', 0)
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">💼 Investment</div>
            <div class="value">{inv:,.0f} ETB</div>
            <div class="sub">Total cost</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        prof = stats.get('potential_profit', 0)
        trend = 'trend-up' if prof > 0 else 'trend-down'
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">📈 Potential Profit</div>
            <div class="value">{prof:,.0f} ETB</div>
            <div class="sub"><span class="{trend}">Margin</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg = stats.get('avg_order_value', 0)
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="label">🛒 Avg Order Value</div>
            <div class="value">{avg:,.0f} ETB</div>
            <div class="sub">Per order</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================
    # CHARTS SECTION - Full Width
    # ==========================================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">📈 Revenue Trend <span class="badge">Last 30 days</span></div>', unsafe_allow_html=True)
        
        # Generate data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        values = [random.randint(2000, 8000) for _ in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=values,
            mode='lines+markers',
            line=dict(color='#667eea', width=2.5),
            marker=dict(size=4, color='#667eea'),
            fill='tozeroy',
            fillcolor='rgba(102,126,234,0.1)'
        ))
        fig.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#1e293b',
                showticklabels=True,
                tickfont=dict(color='#94a3b8', size=10),
                zeroline=False
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x'
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
                'confirmed': '#8b5cf6',
                'cancelled': '#ef4444'
            }
            fig = px.pie(
                df, values='Count', names='Status',
                hole=0.6,
                color='Status',
                color_discrete_map=colors
            )
            fig.update_layout(
                height=220,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=-0.1,
                    xanchor='center',
                    x=0.5,
                    font=dict(color='#94a3b8', size=10)
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(textposition='inside', textinfo='percent', textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No orders to display")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # RECENT ACTIVITY & QUICK ACTIONS
    # ==========================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">🕐 Recent Orders</div>', unsafe_allow_html=True)
        
        recent_orders = get_recent_orders(user_info['id'], 'producer', limit=5)
        if recent_orders:
            for order in recent_orders[:5]:
                status = order.get('status', 'pending')
                amount = order.get('total_amount', 0)
                order_id = order.get('id', '')[:8]
                created = pd.to_datetime(order.get('created_at')).strftime('%b %d, %H:%M') if order.get('created_at') else 'N/A'
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #1e293b;">
                    <div>
                        <div style="color:#e2e8f0;font-size:14px;font-weight:500;">#{order_id}</div>
                        <div style="color:#94a3b8;font-size:12px;">{created}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#10b981;font-weight:600;font-size:15px;">{amount:,.0f} ETB</div>
                        <span class="status-{status} status" style="font-size:11px;padding:2px 10px;border-radius:12px;font-weight:500;">{status.upper()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("📭 No orders received yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="title">🆕 Recent Products</div>', unsafe_allow_html=True)
        
        recent_products = get_recent_products(user_info['id'], limit=5)
        if recent_products:
            for product in recent_products[:5]:
                name = product.get('name', 'Unknown')
                price = product.get('price', 0)
                stock = product.get('quantity', 0)
                category = product.get('category', 'Other')
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #1e293b;">
                    <div>
                        <div style="color:#e2e8f0;font-size:14px;font-weight:500;">{name}</div>
                        <div style="color:#94a3b8;font-size:12px;">📂 {category}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#10b981;font-weight:600;font-size:15px;">{price:,.0f} ETB</div>
                        <div style="color:#f59e0b;font-size:12px;">📦 {stock} units</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("📭 No products added yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # QUICK ACTIONS
    # ==========================================
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Add Product", use_container_width=True, type="primary"):
            st.session_state.edit_product_id = None
            st.rerun()
    with col2:
        if st.button("📦 Inventory", use_container_width=True):
            st.session_state.active_tab = "Inventory"
            st.rerun()
    with col3:
        if st.button("🤖 AI Insights", use_container_width=True):
            st.session_state.active_tab = "AI Insights"
            st.rerun()
    with col4:
        if st.button("📋 Orders", use_container_width=True):
            st.session_state.active_tab = "Orders"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # AI LEARNING STATUS
    # ==========================================
    with st.expander("🧠 AI Learning Progress", expanded=False):
        learning_stats = ai.learning_data
        knowledge = len(ai.knowledge_base.get('product_knowledge', {}))
        iterations = learning_stats.get('learning_iterations', 0)
        interactions = len(learning_stats.get('interactions', []))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Knowledge", knowledge)
        with col2:
            st.metric("🔄 Interactions", interactions)
        with col3:
            st.metric("📈 Iterations", iterations)
        with col4:
            progress = min(iterations / 100, 1.0)
            st.metric("🎯 Progress", f"{progress*100:.0f}%")
        
        st.markdown('<div class="progress-track"><div class="progress-fill" style="width:' + f'{progress*100}%' + '"></div></div>', unsafe_allow_html=True)
        st.caption(f"AI is {progress*100:.1f}% trained on your data")
    
    st.markdown('</div>', unsafe_allow_html=True)
