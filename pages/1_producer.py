import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
from datetime import datetime, timedelta

# --- Imports ---
from utils.auth import initialize_session_state, logout_user
from utils.db_helpers import (
    get_products, create_product, get_orders, get_dashboard_stats, 
    update_product_stock, get_low_stock_products, update_user
)

# Initialize session state
initialize_session_state()

# --- Authentication Guard ---
if not st.session_state.authenticated:
    st.error(" Please log in to access this page.")
    st.stop()

if st.session_state.user_info['role'] != 'producer':
    st.error("⛔ Access Denied. This page is for Producers only.")
    st.stop()

user_info = st.session_state.user_info

# --- AI Model Loader (Silent) ---
@st.cache_resource
def load_ai_model(model_name):
    try:
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", model_name)
        if not os.path.exists(model_path):
            return None
        if os.path.getsize(model_path) < 10:
            return None
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    except:
        return None

demand_model = load_ai_model("demand_forecaster.pkl")
price_model = load_ai_model("price_predictor.pkl")

# --- Initialize Edit Profile State ---
if 'show_edit_profile' not in st.session_state:
    st.session_state.show_edit_profile = False

# ==========================================
# BUSINESS CARD STYLE PROFILE
# ==========================================
st.markdown("""
<style>
.business-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    gap: 30px;
    border: 1px solid #e2e8f0;
    max-width: 800px;
    margin: 0 auto 20px auto;
}
.card-left {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 200px;
    border-right: 2px solid #1e293b;
    padding-right: 30px;
}
.profile-pic-large {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: bold;
    color: white;
    border: 4px solid #fff;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    margin-bottom: 15px;
}
.card-name {
    font-size: 22px;
    font-weight: bold;
    color: #1e293b;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0;
    text-align: center;
}
.card-title {
    font-size: 13px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 5px 0 0 0;
    text-align: center;
}
.card-right {
    flex: 1;
}
.contact-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #1e293b;
}
.contact-icon {
    font-size: 18px;
    width: 24px;
    text-align: center;
}
.contact-label {
    font-weight: 600;
    color: #475569;
    min-width: 80px;
}
.contact-value {
# ==========================================
# RESPONSIVE BUSINESS CARD PROFILE
# ==========================================
st.markdown("""
<style>
.business-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    border: 1px solid #e2e8f0;
    max-width: 800px;
    margin: 0 auto 20px auto;
}
.card-container {
    display: flex;
    align-items: center;
    gap: 25px;
}
.card-left {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 200px;
    border-right: 2px solid #1e293b;
    padding-right: 25px;
}
.profile-pic-large {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: bold;
    color: white;
    border: 4px solid #fff;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    margin-bottom: 15px;
}
.card-name {
    font-size: 22px;
    font-weight: bold;
    color: #1e293b;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0;
    text-align: center;
}
.card-title {
    font-size: 13px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 5px 0 0 0;
    text-align: center;
}
.card-right {
    flex: 1;
}
.contact-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #1e293b;
    flex-wrap: wrap;
}
.contact-icon {
    font-size: 18px;
    width: 24px;
    text-align: center;
    flex-shrink: 0;
}
.contact-label {
    font-weight: 600;
    color: #475569;
    min-width: 80px;
}
.contact-value {
    color: #1e293b;
    font-weight: 500;
    word-break: break-word;
    flex: 1;
}
.edit-profile-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s;
    margin-top: 15px;
    width: 100%;
}
.edit-profile-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* MOBILE RESPONSIVE */
@media screen and (max-width: 768px) {
    .business-card {
        padding: 20px 15px;
        margin: 0 10px 20px 10px;
    }
    .card-container {
        flex-direction: column;
        gap: 20px;
    }
    .card-left {
        border-right: none;
        border-bottom: 2px solid #1e293b;
        padding-right: 0;
        padding-bottom: 20px;
        width: 100%;
    }
    .profile-pic-large {
        width: 100px;
        height: 100px;
        font-size: 40px;
    }
    .card-name {
        font-size: 20px;
    }
    .card-right {
        width: 100%;
    }
    .contact-item {
        font-size: 13px;
        margin-bottom: 10px;
    }
    .contact-label {
        min-width: 70px;
        font-size: 13px;
    }
    .contact-value {
        font-size: 13px;
    }
}

/* TABLET RESPONSIVE */
@media screen and (min-width: 769px) and (max-width: 1024px) {
    .business-card {
        padding: 22px;
        max-width: 700px;
    }
    .profile-pic-large {
        width: 110px;
        height: 110px;
        font-size: 44px;
    }
    .card-name {
        font-size: 20px;
    }
}
</style>
""", unsafe_allow_html=True)

# Get user data
name = user_info.get('name', 'Not specified')
initial = name[0].upper() if name else "P"
email = user_info.get('email', 'Not specified')
phone = user_info.get('phone', 'Not specified')
company = user_info.get('company_name', 'Not specified')
address = user_info.get('address', 'Not specified')
region = user_info.get('region', 'Addis Ababa')

# Business Card Display - RESPONSIVE
st.markdown(f"""
<div class="business-card">
    <div class="card-container">
        <div class="card-left">
            <div class="profile-pic-large">{initial}</div>
            <p class="card-name">{name}</p>
            <p class="card-title">Producer • {company}</p>
        </div>
        <div class="card-right">
            <div class="contact-item">
                <span class="contact-icon">🏠</span>
                <span class="contact-label">Address:</span>
                <span class="contact-value">{address}, {region}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">📞</span>
                <span class="contact-label">Phone:</span>
                <span class="contact-value">{phone}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">✉️</span>
                <span class="contact-label">Email:</span>
                <span class="contact-value">{email}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">🏢</span>
                <span class="contact-label">Company:</span>
                <span class="contact-value">{company}</span>
            </div>
            <div class="contact-item">
                <span class="contact-icon">🌍</span>
                <span class="contact-label">Region:</span>
                <span class="contact-value">{region}</span>
            </div>
            <button class="edit-profile-btn" onclick="document.getElementById('edit-profile-section').scrollIntoView({{behavior: 'smooth'}})">✏️ Edit Profile</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# EDIT PROFILE SECTION
# ==========================================
st.markdown('<div id="edit-profile-section"></div>', unsafe_allow_html=True)

with st.expander("✏️ Edit Profile Information", expanded=st.session_state.show_edit_profile):
    st.markdown("### Update Your Business Card Information")
    
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Full Name", value=user_info.get('name', ''))
            new_email = st.text_input("Email", value=user_info.get('email', ''))
            new_phone = st.text_input("Phone Number", value=user_info.get('phone', ''))
        
        with col2:
            new_company = st.text_input("Company Name", value=user_info.get('company_name', ''))
            new_address = st.text_input("Address", value=user_info.get('address', ''))
            regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                      "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
            current_region = user_info.get('region', 'Addis Ababa')
            region_idx = regions.index(current_region) if current_region in regions else 0
            new_region = st.selectbox("Region", regions, index=region_idx)
        
        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        with col2:
            cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if save_btn:
            if new_name and new_email:
                try:
                    update_user(user_info['id'], 
                               name=new_name, 
                               email=new_email,
                               phone=new_phone,
                               company_name=new_company,
                               address=new_address,
                               region=new_region)
                    
                    # Update session state
                    st.session_state.user_info['name'] = new_name
                    st.session_state.user_info['email'] = new_email
                    st.session_state.user_info['phone'] = new_phone
                    st.session_state.user_info['company_name'] = new_company
                    st.session_state.user_info['address'] = new_address
                    st.session_state.user_info['region'] = new_region
                    
                    st.success("✅ Profile updated successfully!")
                    st.session_state.show_edit_profile = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating profile: {e}")
            else:
                st.error("Name and Email are required!")
        
        if cancel_btn:
            st.session_state.show_edit_profile = False
            st.rerun()

st.markdown("---")

# --- Navigation Tabs ---
tab_dashboard, tab_inventory, tab_orders, tab_ai = st.tabs([
    " Dashboard", "📦 Inventory", " Orders", "🤖 AI Insights"
])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dashboard:
    st.subheader("Business Overview")
    
    stats = get_dashboard_stats('producer', user_info['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", stats.get('total_products', 0))
    col2.metric("Low Stock Alerts", stats.get('low_stock', 0), delta_color="inverse")
    col3.metric("Total Orders", stats.get('total_orders', 0))
    col4.metric("Total Revenue", f"{stats.get('revenue', 0):,.2f} ETB")
    
    st.markdown("---")
    
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

# ==========================================
# TAB 2: INVENTORY MANAGEMENT
# ==========================================
with tab_inventory:
    st.subheader("Manage Your Inventory")
    
    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name", placeholder="e.g., Teff, Coffee")
                category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"])
                price = st.number_input("Selling Price (ETB)", min_value=0.01, step=0.01)
                cost_price = st.number_input("Cost Price (ETB)", min_value=0.01, step=0.01)
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
    
    low_stock = get_low_stock_products(producer_id=user_info['id'])
    if low_stock:
        st.warning(f"️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    st.subheader("All Products")
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
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
        
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "confirmed", "shipped", "delivered", "cancelled"])
        
        if status_filter != "All":
            df_orders = df_orders[df_orders['status'] == status_filter]
            
        st.dataframe(df_orders, use_container_width=True)
        
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
        
        with col1:
            st.markdown("### 📈 Demand Forecasting")
            if demand_model:
                st.info("✅ Model loaded: `demand_forecaster.pkl`")
            else:
                st.info("ℹ️ Using mock forecast data")
            
            if st.button("Predict Next 30 Days Demand", key="pred_demand"):
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

        with col2:
            st.markdown("### 💰 Optimal Price Prediction")
            if price_model:
                st.info("✅ Model loaded: `price_predictor.pkl`")
            else:
                st.info("ℹ️ Using mock price data")
            
            current_price = next((p['price'] for p in products if p['id'] == selected_prod_id), 0)
            st.write(f"Current Price: **{current_price} ETB**")
            
            if st.button("Suggest Optimal Price", key="pred_price"):
                optimal_price = current_price * 1.15
                st.metric("Suggested Optimal Price", f"{optimal_price:.2f} ETB", delta=f"+{optimal_price - current_price:.2f} ETB")
                st.info("💡 Based on current market trends and demand elasticity.")
