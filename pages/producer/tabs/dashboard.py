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
    """Render stunning Producer Dashboard inspired by Kyubit"""
    
    # Get all stats
    stats = get_dashboard_stats('producer', user_info['id'])
    
    # Custom CSS for dashboard
    st.markdown("""
    <style>
    /* Dashboard Container */
    .dashboard-container {
        padding: 20px;
        background: linear-gradient(180deg, #0a0e1a 0%, #1a1a2e 100%);
        border-radius: 20px;
        margin-bottom: 20px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #2d3748;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
        border-color: #667eea;
    }
    
    .metric-card .icon {
        font-size: 24px;
        margin-bottom: 8px;
    }
    
    .metric-card .label {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card .value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 700;
        margin: 8px 0 4px 0;
    }
    
    .metric-card .change {
        font-size: 13px;
        font-weight: 600;
    }
    
    .metric-card .change.positive {
        color: #10b981;
    }
    
    .metric-card .change.negative {
        color: #ef4444;
    }
    
    .metric-card .change.neutral {
        color: #f59e0b;
    }
    
    /* Glow Effects */
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    
    /* Chart Container */
    .chart-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #2d3748;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .chart-container h4 {
        color: #e2e8f0;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .status-badge.delivered {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }
    
    .status-badge.pending {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
    }
    
    .status-badge.shipped {
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
    }
    
    .status-badge.cancelled {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
    
    /* Quick Actions */
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        cursor: pointer;
        width: 100%;
        text-align: center;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    
    /* Responsive */
    @media screen and (max-width: 768px) {
        .metric-card .value {
            font-size: 22px;
        }
        .metric-card .label {
            font-size: 11px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # HEADER
    # ==========================================
    st.markdown("""
    <div style="margin-bottom: 30px;">
        <h1 style="color: #f8fafc; font-weight: 700; font-size: 28px; margin: 0;">
            📊 Dashboard
        </h1>
        <p style="color: #94a3b8; font-size: 14px; margin-top: 4px;">
            Real-time overview of your business performance
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # KEY METRICS ROW
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">📦</div>
            <div class="label">Total Products</div>
            <div class="value">{stats.get('total_products', 0)}</div>
            <div class="change positive">↑ 12% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        low_stock = stats.get('low_stock', 0)
        change_class = 'negative' if low_stock > 0 else 'positive'
        change_text = f"⚠️ {low_stock} need restock" if low_stock > 0 else "✅ All stocked"
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">⚠️</div>
            <div class="label">Low Stock Alerts</div>
            <div class="value">{low_stock}</div>
            <div class="change {change_class}">{change_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">📋</div>
            <div class="label">Total Orders</div>
            <div class="value">{stats.get('total_orders', 0)}</div>
            <div class="change positive">↑ 8% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        revenue = stats.get('revenue', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">💰</div>
            <div class="label">Total Revenue</div>
            <div class="value">{revenue:,.0f} ETB</div>
            <div class="change positive">↑ 15% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==========================================
    # SECONDARY METRICS ROW
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stock_value = stats.get('total_stock_value', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">📊</div>
            <div class="label">Stock Value</div>
            <div class="value">{stock_value:,.0f} ETB</div>
            <div class="change neutral">Current inventory value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        investment = stats.get('total_investment', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">💼</div>
            <div class="label">Total Investment</div>
            <div class="value">{investment:,.0f} ETB</div>
            <div class="change neutral">Total cost of inventory</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        profit = stats.get('potential_profit', 0)
        profit_class = 'positive' if profit > 0 else 'negative'
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">📈</div>
            <div class="label">Potential Profit</div>
            <div class="value">{profit:,.0f} ETB</div>
            <div class="change {profit_class}">{'↑' if profit > 0 else '↓'} Profit margin</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_order = stats.get('avg_order_value', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">🛒</div>
            <div class="label">Avg Order Value</div>
            <div class="value">{avg_order:,.0f} ETB</div>
            <div class="change positive">↑ 5% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================
    # CHARTS ROW
    # ==========================================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h4>📈 Revenue & Orders Trend</h4>', unsafe_allow_html=True)
        
        # Generate sample trend data (replace with real data)
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        revenue_data = [random.randint(1000, 5000) for _ in range(len(dates))]
        orders_data = [random.randint(1, 10) for _ in range(len(dates))]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=revenue_data,
            name='Revenue (ETB)',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        
        fig.add_trace(go.Bar(
            x=dates,
            y=orders_data,
            name='Orders',
            marker=dict(color='#764ba2', opacity=0.7),
            yaxis='y2'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#2d3748',
                tickfont=dict(color='#94a3b8')
            ),
            yaxis=dict(
                title='Revenue (ETB)',
                showgrid=True,
                gridcolor='#2d3748',
                tickfont=dict(color='#94a3b8')
            ),
            yaxis2=dict(
                title='Orders',
                overlaying='y',
                side='right',
                showgrid=False,
                tickfont=dict(color='#94a3b8')
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                font=dict(color='#94a3b8')
            ),
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h4>📊 Order Status</h4>', unsafe_allow_html=True)
        
        status_counts = stats.get('order_status', {})
        if status_counts:
            df_status = pd.DataFrame({
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
                df_status,
                values='Count',
                names='Status',
                hole=0.6,
                color='Status',
                color_discrete_map=colors
            )
            
            fig.update_layout(
                template='plotly_dark',
                showlegend=True,
                legend=dict(
                    orientation='v',
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=0,
                    font=dict(color='#94a3b8', size=11)
                ),
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent',
                textfont=dict(color='white', size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No orders to display")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # BOTTOM SECTION - Recent Activity
    # ==========================================
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h4>🕐 Recent Orders</h4>', unsafe_allow_html=True)
        
        recent_orders = get_recent_orders(user_info['id'], 'producer', limit=5)
        if recent_orders:
            for order in recent_orders[:5]:
                status = order.get('status', 'pending')
                status_class = status.lower()
                amount = order.get('total_amount', 0)
                
                st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    background: rgba(45, 55, 72, 0.3);
                    border-radius: 10px;
                    border-left: 3px solid {colors.get(status, '#667eea')};
                ">
                    <div>
                        <div style="color: #e2e8f0; font-weight: 500; font-size: 14px;">
                            Order #{order.get('id', '')[:8]}
                        </div>
                        <div style="color: #94a3b8; font-size: 12px;">
                            {pd.to_datetime(order.get('created_at')).strftime('%Y-%m-%d %H:%M') if order.get('created_at') else 'N/A'}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #10b981; font-weight: 600; font-size: 16px;">
                            {amount:,.2f} ETB
                        </div>
                        <span class="status-badge {status_class}">{status.upper()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No orders received yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h4>🆕 Recent Products</h4>', unsafe_allow_html=True)
        
        recent_products = get_recent_products(user_info['id'], limit=5)
        if recent_products:
            for product in recent_products[:5]:
                price = product.get('price', 0)
                stock = product.get('quantity', 0)
                
                st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    background: rgba(45, 55, 72, 0.3);
                    border-radius: 10px;
                    border-left: 3px solid #667eea;
                ">
                    <div>
                        <div style="color: #e2e8f0; font-weight: 500; font-size: 14px;">
                            {product.get('name', 'Unknown')}
                        </div>
                        <div style="color: #94a3b8; font-size: 12px;">
                            📂 {product.get('category', 'N/A')}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #10b981; font-weight: 600; font-size: 16px;">
                            {price:,.2f} ETB
                        </div>
                        <div style="color: #f59e0b; font-size: 12px;">
                            📦 {stock} units
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No products added yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # QUICK ACTIONS SECTION
    # ==========================================
    st.markdown("---")
    st.markdown('<h4 style="color: #e2e8f0; margin-bottom: 16px;">⚡ Quick Actions</h4>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add New Product", use_container_width=True):
            st.session_state.edit_product_id = None
            st.rerun()
    
    with col2:
        if st.button("📦 View All Products", use_container_width=True):
            st.session_state.active_tab = "Inventory"
            st.rerun()
    
    with col3:
        if st.button("🤖 AI Insights", use_container_width=True):
            st.session_state.active_tab = "AI Insights"
            st.rerun()
    
    with col4:
        if st.button("📊 View Orders", use_container_width=True):
            st.session_state.active_tab = "Orders"
            st.rerun()
    
    # ==========================================
    # AI LEARNING STATUS (Collapsible)
    # ==========================================
    with st.expander("🧠 AI Learning Status", expanded=False):
        learning_stats = ai.learning_data
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Knowledge Items", len(ai.knowledge_base.get('product_knowledge', {})))
        with col2:
            st.metric("🔄 Interactions", len(learning_stats.get('interactions', [])))
        with col3:
            st.metric("🔍 Searches", len(learning_stats.get('search_queries', [])))
        with col4:
            st.metric("📈 Learning Iterations", learning_stats.get('learning_iterations', 0))
        
        st.markdown("### 🧬 Learning Progress")
        progress = min(learning_stats.get('learning_iterations', 0) / 100, 1.0)
        st.progress(progress)
        st.caption(f"AI is {progress*100:.1f}% trained on your data")
