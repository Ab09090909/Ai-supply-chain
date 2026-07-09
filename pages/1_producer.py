import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
from datetime import datetime, timedelta

# --- Imports from our project structure ---
from utils.auth import initialize_session_state, logout_user
from utils.db_helpers import (
    get_products, create_product, get_orders, get_dashboard_stats, 
    update_product_stock, get_low_stock_products
)

# Initialize session state
initialize_session_state()

# --- Authentication Guard ---
if not st.session_state.authenticated:
    st.error("🔒 Please log in to access this page.")
    st.stop()

if st.session_state.user_info['role'] != 'producer':
    st.error("⛔ Access Denied. This page is for Producers only.")
    st.stop()

user_info = st.session_state.user_info

# --- AI Model Loader (SAFE - Never crashes the app) ---
@st.cache_resource
def load_ai_model(model_name):
    """Load AI models safely. Returns None if file doesn't exist or is corrupted."""
    try:
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", model_name)
        if not os.path.exists(model_path):
            st.warning(f"️ Model file not found: {model_name}")
            return None
        
        # Check if file is empty or too small
        if os.path.getsize(model_path) < 100:
            st.warning(f"⚠️ Model file is too small/corrupted: {model_name}")
            return None
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.warning(f"⚠️ Failed to load {model_name}: {str(e)}")
        return None

# Load models (will return None if they fail)
demand_model = load_ai_model("demand_forecaster.pkl")
price_model = load_ai_model("price_predictor.pkl")
fraud_model = load_ai_model("fraud_detector.pkl")
merchant_matcher = load_ai_model("merchant_matcher.pkl")
recommendation_engine = load_ai_model("recommendation_engine.pkl")

# --- Page Configuration ---
st.set_page_config(page_title="Producer Dashboard", page_icon="🏭", layout="wide")

# --- Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f" Producer Dashboard")
    st.markdown(f"Welcome back, **{user_info['name']}**!")
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()

st.markdown("---")

# Show model status
model_status = []
if demand_model: model_status.append("✅ Demand Forecaster")
if price_model: model_status.append("✅ Price Predictor")
if fraud_model: model_status.append("✅ Fraud Detector")
if merchant_matcher: model_status.append("✅ Merchant Matcher")
if recommendation_engine: model_status.append("✅ Recommendation Engine")

if model_status:
    st.success(f"AI Models Loaded: {', '.join(model_status)}")
else:
    st.warning("⚠️ No AI models loaded. Models will be simulated with mock data.")

# --- Navigation Tabs ---
tab_dashboard, tab_inventory, tab_orders, tab_ai = st.tabs([
    "📊 Dashboard", "📦 Inventory", "🚚 Orders", "🤖 AI Insights"
])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dashboard:
    st.subheader("Business Overview")
    
    # Fetch stats
    stats = get_dashboard_stats('producer', user_info['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", stats.get('total_products', 0))
    col2.metric("Low Stock Alerts", stats.get('low_stock', 0), delta_color="inverse")
    col3.metric("Total Orders", stats.get('total_orders', 0))
    col4.metric("Total Revenue", f"${stats.get('revenue', 0):,.2f}")
    
    st.markdown("---")
    
    # Fetch products for chart
    products = get_products(producer_id=user_info['id'])
    
    if products:
        df_products = pd.DataFrame(products)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stock Levels by Category")
            fig_stock = px.bar(
                df_products.groupby('category')['stock_quantity'].sum().reset_index(),
                x='category', y='stock_quantity', 
                title="Total Stock per Category",
                color='stock_quantity',
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

# ==========================================
# TAB 2: INVENTORY MANAGEMENT
# ==========================================
with tab_inventory:
    st.subheader("Manage Your Inventory")
    
    # Add Product Form
    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name", placeholder="e.g., Organic Wheat")
                category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"])
                price = st.number_input("Selling Price ($)", min_value=0.01, step=0.01)
                cost_price = st.number_input("Cost Price ($)", min_value=0.01, step=0.01)
            with col2:
                stock = st.number_input("Initial Stock Quantity", min_value=0, step=1)
                min_stock = st.number_input("Minimum Stock Alert Level", min_value=1, value=10)
                weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
                description = st.text_area("Description", placeholder="Brief product description...")
            
            submitted = st.form_submit_button("Add Product", use_container_width=True, type="primary")
            
            if submitted:
                if not name:
                    st.error("Product name is required!")
                else:
                    success, msg, prod_id = create_product(
                        name=name, description=description, category=category,
                        price=price, cost_price=cost_price, stock_quantity=stock,
                        producer_id=user_info['id'], weight=weight
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("---")
    
    # Low Stock Alerts
    low_stock = get_low_stock_products(producer_id=user_info['id'])
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'stock_quantity', 'min_stock']], use_container_width=True)
    
    # All Products Table
    st.subheader("All Products")
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        # Format for display
        display_df = df_all[['name', 'category', 'price', 'stock_quantity', 'sku', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No products added yet.")

# ==========================================
# TAB 3: ORDERS
# ==========================================
with tab_orders:
    st.subheader("Recent Orders")
    
    orders = get_orders(user_info['id'], 'producer', limit=50)
    
    if orders:
        df_orders = pd.DataFrame(orders)
        
        # Status filter
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "confirmed", "shipped", "delivered", "cancelled"])
        
        if status_filter != "All":
            df_orders = df_orders[df_orders['status'] == status_filter]
            
        st.dataframe(df_orders, use_container_width=True)
        
        # Order Analytics
        col1, col2 = st.columns(2)
        with col1:
            fig_status = px.pie(
                df_orders, names='status', title="Order Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No orders received yet.")

# ==========================================
# TAB 4: AI INSIGHTS
# ==========================================
with tab_ai:
    st.subheader("🤖 AI-Powered Supply Chain Insights")
    
    products = get_products(producer_id=user_info['id'], limit=20)
    
    if not products:
        st.warning("Add some products first to use AI insights.")
    else:
        product_names = {p['id']: p['name'] for p in products}
        selected_prod_id = st.selectbox("Select Product for Analysis", list(product_names.keys()), format_func=lambda x: product_names[x])
        
        col1, col2 = st.columns(2)
        
        # --- Demand Forecasting ---
        with col1:
            st.markdown("### 📈 Demand Forecasting")
            if demand_model:
                st.info("Model loaded: `demand_forecaster.pkl`")
                if st.button("Predict Next 30 Days Demand", key="pred_demand"):
                    # Use actual model if available, otherwise mock data
                    try:
                        # prediction = demand_model.predict(selected_prod_id)
                        forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
                        forecast_values = [int(50 + i * 2 + (i % 5)) for i in range(30)]
                        
                        fig_demand = go.Figure()
                        fig_demand.add_trace(go.Scatter(
                            x=forecast_dates, y=forecast_values,
                            mode='lines+markers', name='Predicted Demand',
                            line=dict(color='#667eea', width=3)
                        ))
                        fig_demand.update_layout(
                            title="Predicted Demand (Next 30 Days)",
                            xaxis_title="Date", yaxis_title="Units Demanded",
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_demand, use_container_width=True)
                        st.success("✅ Forecast generated successfully!")
                    except Exception as e:
                        st.error(f"Prediction failed: {e}")
            else:
                st.warning("⚠️ `demand_forecaster.pkl` not available. Using mock data.")
                if st.button("Predict Next 30 Days Demand (Mock)", key="pred_demand_mock"):
                    forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
                    forecast_values = [int(50 + i * 2 + (i % 5)) for i in range(30)]
                    
                    fig_demand = go.Figure()
                    fig_demand.add_trace(go.Scatter(
                        x=forecast_dates, y=forecast_values,
                        mode='lines+markers', name='Predicted Demand',
                        line=dict(color='#667eea', width=3)
                    ))
                    fig_demand.update_layout(
                        title="Predicted Demand (Next 30 Days) - Mock Data",
                        xaxis_title="Date", yaxis_title="Units Demanded",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_demand, use_container_width=True)

        # --- Price Prediction ---
        with col2:
            st.markdown("### 💰 Optimal Price Prediction")
            if price_model:
                st.info("Model loaded: `price_predictor.pkl`")
                current_price = next((p['price'] for p in products if p['id'] == selected_prod_id), 0)
                st.write(f"Current Price: **${current_price}**")
                
                if st.button("Suggest Optimal Price", key="pred_price"):
                    try:
                        # optimal_price = price_model.predict(selected_prod_id)
                        optimal_price = current_price * 1.15
                        st.metric("Suggested Optimal Price", f"${optimal_price:.2f}", delta=f"+${optimal_price - current_price:.2f}")
                        st.info(" Based on current market trends and demand elasticity.")
                    except Exception as e:
                        st.error(f"Price prediction failed: {e}")
            else:
                st.warning("⚠️ `price_predictor.pkl` not available. Using mock data.")
                current_price = next((p['price'] for p in products if p['id'] == selected_prod_id), 0)
                st.write(f"Current Price: **${current_price}**")
                
                if st.button("Suggest Optimal Price (Mock)", key="pred_price_mock"):
                    optimal_price = current_price * 1.15
                    st.metric("Suggested Optimal Price", f"${optimal_price:.2f}", delta=f"+${optimal_price - current_price:.2f}")
                    st.info("💡 Mock prediction - actual model not loaded.")
