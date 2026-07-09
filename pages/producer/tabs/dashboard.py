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
    """Render clean compact Producer Dashboard"""
    
    # Get all stats
    stats = get_dashboard_stats('producer', user_info['id'])
    
    # Compact CSS
    st.markdown("""
    <style>
    /* Compact metrics */
    .metric-compact {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid #2d3748;
        text-align: center;
    }
    .metric-compact .label {
        color: #94a3b8;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-compact .value {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 700;
        margin: 4px 0;
    }
    .metric-compact .change {
        font-size: 11px;
        font-weight: 500;
    }
    .metric-compact .change.positive { color: #10b981; }
    .metric-compact .change.negative { color: #ef4444; }
    .metric-compact .change.neutral { color: #f59e0b; }
    
    /* Compact chart container */
    .chart-compact {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid #2d3748;
        margin-bottom: 8px;
    }
    .chart-compact h5 {
        color: #e2e8f0;
        font-size: 13px;
        font-weight: 600;
        margin: 0 0 8px 0;
    }
    
    /* Status badges compact */
    .badge-sm {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
    }
    .badge-sm.delivered { background: rgba(16,185,129,0.2); color: #10b981; }
    .badge-sm.pending { background: rgba(245,158,11,0.2); color: #f59e0b; }
    .badge-sm.shipped { background: rgba(59,130,246,0.2); color: #3b82f6; }
    .badge-sm.cancelled { background: rgba(239,68,68,0.2); color: #ef4444; }
    
    /* Activity item compact */
    .activity-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 10px;
        margin-bottom: 4px;
        background: rgba(45, 55, 72, 0.2);
        border-radius: 6px;
        border-left: 2px solid #667eea;
    }
    .activity-item .name {
        color: #e2e8f0;
        font-size: 13px;
        font-weight: 500;
    }
    .activity-item .detail {
        color: #94a3b8;
        font-size: 11px;
    }
    .activity-item .amount {
        color: #10b981;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Remove extra spacing */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # METRICS - 2 Rows of 4
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">📦 Products</div>
            <div class="value">{stats.get('total_products', 0)}</div>
            <div class="change positive">↑ Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        low = stats.get('low_stock', 0)
        cls = 'negative' if low > 0 else 'positive'
        txt = f'⚠️ {low}' if low > 0 else '✅ OK'
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">⚠️ Low Stock</div>
            <div class="value">{low}</div>
            <div class="change {cls}">{txt}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">📋 Orders</div>
            <div class="value">{stats.get('total_orders', 0)}</div>
            <div class="change positive">↑ Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rev = stats.get('revenue', 0)
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">💰 Revenue</div>
            <div class="value">{rev:,.0f}</div>
            <div class="change positive">↑ ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        val = stats.get('total_stock_value', 0)
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">📊 Stock Value</div>
            <div class="value">{val:,.0f}</div>
            <div class="change neutral">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        inv = stats.get('total_investment', 0)
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">💼 Investment</div>
            <div class="value">{inv:,.0f}</div>
            <div class="change neutral">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        prof = stats.get('potential_profit', 0)
        cls = 'positive' if prof > 0 else 'negative'
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">📈 Profit</div>
            <div class="value">{prof:,.0f}</div>
            <div class="change {cls}">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg = stats.get('avg_order_value', 0)
        st.markdown(f"""
        <div class="metric-compact">
            <div class="label">🛒 Avg Order</div>
            <div class="value">{avg:,.0f}</div>
            <div class="change neutral">ETB</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================
    # CHARTS - Compact Row
    # ==========================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-compact"><h5>📈 Revenue Trend</h5>', unsafe_allow_html=True)
        
        # Generate trend data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        values = [random.randint(2000, 8000) for _ in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=values,
            mode='lines',
            line=dict(color='#667eea', width=2),
            fill='tozeroy',
            fillcolor='rgba(102,126,234,0.15)'
        ))
        fig.update_layout(
            height=180,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-compact"><h5>📊 Order Status</h5>', unsafe_allow_html=True)
        
        status_counts = stats.get('order_status', {})
        if status_counts:
            df = pd.DataFrame({
                'Status': list(status_counts.keys()),
                'Count': list(status_counts.values())
            })
            colors = {'delivered':'#10b981','pending':'#f59e0b','shipped':'#3b82f6','cancelled':'#ef4444'}
            fig = px.pie(df, values='Count', names='Status', hole=0.5, color='Status', color_discrete_map=colors)
            fig.update_layout(
                height=180,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(textposition='inside', textinfo='percent', textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No orders yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # RECENT ACTIVITY - Compact
    # ==========================================
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-compact"><h5>🕐 Recent Orders</h5>', unsafe_allow_html=True)
        
        recent_orders = get_recent_orders(user_info['id'], 'producer', limit=4)
        if recent_orders:
            for order in recent_orders[:4]:
                status = order.get('status', 'pending')
                amount = order.get('total_amount', 0)
                order_id = order.get('id', '')[:8]
                st.markdown(f"""
                <div class="activity-item">
                    <div>
                        <div class="name">#{order_id}</div>
                        <div class="detail">{pd.to_datetime(order.get('created_at')).strftime('%m/%d') if order.get('created_at') else 'N/A'}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="amount">{amount:,.0f} ETB</div>
                        <span class="badge-sm {status}">{status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("📭 No orders")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-compact"><h5>🆕 Recent Products</h5>', unsafe_allow_html=True)
        
        recent_products = get_recent_products(user_info['id'], limit=4)
        if recent_products:
            for product in recent_products[:4]:
                name = product.get('name', 'Unknown')
                price = product.get('price', 0)
                stock = product.get('quantity', 0)
                st.markdown(f"""
                <div class="activity-item">
                    <div>
                        <div class="name">{name}</div>
                        <div class="detail">📂 {product.get('category', 'N/A')}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="amount">{price:,.0f} ETB</div>
                        <div class="detail">📦 {stock}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("📭 No products")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # QUICK ACTIONS - Compact
    # ==========================================
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add", use_container_width=True, type="primary"):
            st.session_state.edit_product_id = None
            st.rerun()
    with col2:
        if st.button("📦 Products", use_container_width=True):
            st.session_state.active_tab = "Inventory"
            st.rerun()
    with col3:
        if st.button("🤖 AI", use_container_width=True):
            st.session_state.active_tab = "AI Insights"
            st.rerun()
    with col4:
        if st.button("📋 Orders", use_container_width=True):
            st.session_state.active_tab = "Orders"
            st.rerun()
    
    # ==========================================
    # AI STATUS - Collapsible
    # ==========================================
    with st.expander("🧠 AI Learning", expanded=False):
        learning_stats = ai.learning_data
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Knowledge", len(ai.knowledge_base.get('product_knowledge', {})))
        with col2:
            st.metric("🔄 Interactions", len(learning_stats.get('interactions', [])))
        with col3:
            st.metric("📈 Iterations", learning_stats.get('learning_iterations', 0))
        with col4:
            progress = min(learning_stats.get('learning_iterations', 0) / 100, 1.0)
            st.metric("🎯 Progress", f"{progress*100:.0f}%")
        st.progress(progress)
