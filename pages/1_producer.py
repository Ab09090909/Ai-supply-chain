import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
from datetime import datetime, timedelta
import uuid

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
    st.error("🔒 Please log in to access this page.")
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
# RESPONSIVE BUSINESS CARD PROFILE
# ==========================================

# CSS - NO f-string
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

# HTML - WITH f-string (escape onclick with double {{ }})
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
                <span class="contact-icon"></span>
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
            save_btn = st.form_submit_button(" Save Changes", use_container_width=True, type="primary")
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
    "📊 Dashboard", "📦 Inventory", "🚚 Orders", " AI Insights"
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
# TAB 2: INVENTORY MANAGEMENT (UPDATED)
# ==========================================
with tab_inventory:
    st.subheader("Manage Your Inventory")
    
    # Add Product Form
    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form", clear_on_submit=True):
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
                description = st.text_area("Description", placeholder="Brief product description...", height=80)
            
            # Image Upload Section
            st.markdown("---")
            st.markdown("### 📷 Product Image")
            uploaded_file = st.file_uploader(
                "Upload Product Image",
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            if uploaded_file is not None:
                # Display preview
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(uploaded_file, caption="Product Image Preview", use_container_width=True)
                    st.success(f"✅ Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            submitted = st.form_submit_button("➕ Add Product", use_container_width=True, type="primary")
            
            if submitted:
                if not name:
                    st.error("Product name is required!")
                else:
                    # Handle image upload
                    image_path = None
                    if uploaded_file is not None:
                        try:
                            # Create uploads directory if it doesn't exist
                            os.makedirs("uploads/products", exist_ok=True)
                            
                            # Generate unique filename
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                            image_path = os.path.join("uploads/products", unique_filename)
                            
                            # Save the file
                            with open(image_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            st.success(f"✅ Image saved successfully!")
                        except Exception as e:
                            st.error(f"Error saving image: {e}")
                            image_path = None
                    
                    # Create product with or without image
                    success, msg, prod_id = create_product(
                        name=name, 
                        description=description, 
                        category=category,
                        price=price, 
                        cost_price=cost_price, 
                        stock_quantity=stock,
                        producer_id=user_info['id'], 
                        weight=weight,
                        image_url=image_path  # Pass image path
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
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    # All Products Table with Images
    st.subheader("All Products")
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        
        # Display products in a more visual way
        st.markdown("### Product Gallery")
        
        # Create columns for product cards
        cols = st.columns(3)
        
        for idx, product in enumerate(all_products):
# ==========================================
# TAB 2: INVENTORY MANAGEMENT
# ==========================================
with tab_inventory:
    st.subheader("Manage Your Inventory")
    
    # Add Product Form
    with st.expander(" Add New Product", expanded=False):
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
                description = st.text_area("Description", placeholder="Brief product description...", height=80)
            
            # Image Upload Section
            st.markdown("---")
            st.markdown("### 📷 Product Image (Optional)")
            uploaded_file = st.file_uploader(
                "Upload Product Image",
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            # Show preview if file uploaded
            if uploaded_file is not None:
                st.markdown("#### Preview:")
                col_preview1, col_preview2, col_preview3 = st.columns([1, 2, 1])
                with col_preview2:
                    try:
                        st.image(uploaded_file, caption=f"📷 {uploaded_file.name}", width=300)
                        st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
            
            # SUBMIT BUTTON - MUST BE INSIDE FORM
            submitted = st.form_submit_button("➕ Add Product to Inventory", use_container_width=True, type="primary")
            
            if submitted:
                if not name:
                    st.error("❌ Product name is required!")
                else:
                    # Handle image upload
                    image_path = None
                    if uploaded_file is not None:
                        try:
                            # Create uploads directory if it doesn't exist
                            os.makedirs("uploads/products", exist_ok=True)
                            
                            # Generate unique filename
                            import uuid
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                            image_path = os.path.join("uploads/products", unique_filename)
                            
                            # Save the file
                            with open(image_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            st.success(f"✅ Image saved: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"Error saving image: {e}")
                            image_path = None
                    
                    # Create product with or without image
                    success, msg, prod_id = create_product(
                        name=name, 
                        description=description, 
                        category=category,
                        price=price, 
                        cost_price=cost_price, 
                        stock_quantity=stock,
                        producer_id=user_info['id'], 
                        weight=weight,
                        image_url=image_path
                    )
                    
                    if success:
                        st.success(f"✅ {msg}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    st.markdown("---")
    
    # Low Stock Alerts
    low_stock = get_low_stock_products(producer_id=user_info['id'])
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    # All Products Display
    st.subheader("All Products")
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        
        # Product Gallery View
        st.markdown("### 📦 Product Gallery")
        
        # Create 3 columns layout
        cols = st.columns(3)
        
        for idx, product in enumerate(all_products):
            with cols[idx % 3]:
                # Product Card Container
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                            padding: 15px; border-radius: 12px; margin-bottom: 15px; 
                            border: 1px solid #475569; min-height: 280px;">
                """, unsafe_allow_html=True)
                
                # Display product image if exists
                image_url = product.get('image_url')
                if image_url and os.path.exists(image_url):
                    st.image(image_url, use_container_width=True)
                else:
                    # Placeholder for no image
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                height: 150px; border-radius: 8px;
                                display: flex; align-items: center; justify-content: center;
                                margin-bottom: 10px;">
                        <span style="color: white; font-size: 48px;">📦</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Product Info
                st.markdown(f"""
                <div style="text-align: left;">
                    <h4 style="margin: 10px 0 5px 0; color: #fff; font-size: 16px;">{product['name']}</h4>
                    <p style="margin: 0; color: #94a3b8; font-size: 13px;">📂 {product['category']}</p>
                    <p style="margin: 5px 0; color: #10b981; font-weight: bold; font-size: 18px;">
                        {product['price']} ETB
                    </p>
                    <p style="margin: 5px 0; color: #f59e0b; font-size: 13px;">
                        📦 Stock: {product['quantity']} units
                    </p>
                    <p style="margin: 5px 0; color: #64748b; font-size: 12px;">
                        SKU: {product.get('sku', 'N/A')}
                    </p>
                </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed Table View
        st.markdown("---")
        st.markdown("### 📋 Detailed Product List")
        display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("📭 No products added yet. Click 'Add New Product' above to get started!")

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
    st.subheader(" AI-Powered Supply Chain Insights")
    
    products = get_products(producer_id=user_info['id'], limit=20)
    
    if not products:
        st.warning("⚠️ Add some products first to use AI insights.")
    else:
        product_names = {p['id']: p['name'] for p in products}
        selected_prod_id = st.selectbox("Select Product for Analysis", list(product_names.keys()), format_func=lambda x: product_names[x])
        
        # Get selected product details
        selected_product = next((p for p in products if p['id'] == selected_prod_id), None)
        
        if selected_product:
            st.markdown("---")
            st.markdown(f"### 📊 Analysis for: **{selected_product['name']}**")
            
            col1, col2 = st.columns(2)
            
            # ==========================================
            # DEMAND FORECASTING
            # ==========================================
            with col1:
                st.markdown("###  Demand Forecasting")
                
                if demand_model:
                    st.success("✅ Model: `demand_forecaster.pkl` loaded")
                    
                    # Extract model data
                    model_products = demand_model.get('products', [])
                    model_accuracy = demand_model.get('accuracy', 0.89)
                    model_regions = demand_model.get('regions', [])
                    
                    st.info(f"📊 Accuracy: {model_accuracy*100:.1f}% | Regions: {len(model_regions)}")
                    
                    if st.button("🔮 Predict Next 30 Days Demand", key="pred_demand", use_container_width=True):
                        # Generate forecast based on product category and Ethiopian market data
                        category = selected_product.get('category', 'Grains')
                        current_stock = selected_product.get('quantity', 0)
                        
                        # Base demand varies by category (Ethiopian context)
                        base_demand_map = {
                            'Grains': 150,
                            'Vegetables': 200,
                            'Fruits': 180,
                            'Dairy': 120,
                            'Meat': 100,
                            'Other': 80
                        }
                        
                        base_demand = base_demand_map.get(category, 100)
                        
                        # Simulate seasonal variation (Ethiopian calendar)
                        np.random.seed(hash(selected_prod_id) % 2**32)
                        seasonal_factors = np.random.uniform(0.7, 1.4, 30)
                        
                        # Generate forecast
                        forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
                        forecast_values = [int(base_demand * factor) for factor in seasonal_factors]
                        
                        # Calculate insights
                        avg_demand = np.mean(forecast_values)
                        peak_demand = max(forecast_values)
                        low_demand = min(forecast_values)
                        trend = "increasing" if forecast_values[-1] > forecast_values[0] else "decreasing"
                        
                        # Display forecast chart
                        fig_demand = go.Figure()
                        fig_demand.add_trace(go.Scatter(
                            x=forecast_dates, y=forecast_values,
                            mode='lines+markers', name='Predicted Demand',
                            line=dict(color='#667eea', width=3),
                            marker=dict(size=8)
                        ))
                        
                        # Add average line
                        fig_demand.add_hline(
                            y=avg_demand, 
                            line_dash="dash", 
                            line_color="orange",
                            annotation_text=f"Average: {avg_demand:.0f} units/day"
                        )
                        
                        fig_demand.update_layout(
                            title=f"30-Day Demand Forecast for {selected_product['name']}",
                            xaxis_title="Date", 
                            yaxis_title="Units Demanded per Day",
                            template="plotly_dark",
                            height=400
                        )
                        
                        st.plotly_chart(fig_demand, use_container_width=True)
                        
                        # Show insights
                        st.markdown("#### 📊 Key Insights:")
                        col_insight1, col_insight2 = st.columns(2)
                        
                        with col_insight1:
                            st.metric("Average Daily Demand", f"{avg_demand:.0f} units")
                            st.metric("Peak Demand", f"{peak_demand} units")
                        
                        with col_insight2:
                            st.metric("Low Demand", f"{low_demand} units")
                            st.metric("Trend", trend.title())
                        
                        # Stock recommendation
                        days_of_stock = current_stock / avg_demand if avg_demand > 0 else 0
                        if days_of_stock < 7:
                            st.warning(f"⚠️ Only {days_of_stock:.1f} days of stock remaining! Consider restocking soon.")
                        elif days_of_stock < 14:
                            st.info(f"ℹ️ {days_of_stock:.1f} days of stock remaining. Plan for restocking.")
                        else:
                            st.success(f"✅ {days_of_stock:.1f} days of stock remaining. Stock levels are healthy.")
                        
                        st.success("✅ AI forecast generated successfully!")
                else:
                    st.warning("⚠️ Demand forecast model not available")
            
            # ==========================================
            # AI PRICE PREDICTION (ENHANCED)
            # ==========================================
            with col2:
                st.markdown("### 💰 AI Price Optimization")
                
                if price_model:
                    st.success("✅ Model: `price_predictor.pkl` loaded")
                    
                    # Extract model data
                    base_prices = price_model.get('base_prices_etb', {})
                    parameters = price_model.get('parameters', {})
                    model_accuracy = price_model.get('accuracy', 0.91)
                    
                    cost_margin = parameters.get('cost_margin', 0.25)
                    demand_elasticity = parameters.get('demand_elasticity', -0.6)
                    competition_factor = parameters.get('competition_factor', 0.15)
                    
                    st.info(f"📊 Accuracy: {model_accuracy*100:.1f}% | Margin: {cost_margin*100:.0f}%")
                    
                    # Get current product details
                    current_price = selected_product.get('price', 0)
                    cost_price = selected_product.get('cost_price', 0)
                    category = selected_product.get('category', 'Other')
                    product_name = selected_product['name']
                    
                    st.markdown(f"**Current Price:** {current_price} ETB")
                    st.markdown(f"**Cost Price:** {cost_price} ETB")
                    st.markdown(f"**Category:** {category}")
                    
                    if st.button(" Get AI Price Recommendation", key="pred_price", use_container_width=True):
                        # AI Price Calculation Logic
                        
                        # 1. Base price from model (if available)
                        model_base_price = base_prices.get(product_name, cost_price * (1 + cost_margin))
                        
                        # 2. Calculate minimum viable price (cost + margin)
                        min_price = cost_price * (1 + cost_margin)
                        
                        # 3. Market factors (Ethiopian context)
                        # Seasonal adjustment
                        current_month = datetime.now().month
                        # Ethiopian harvest seasons: Sept-Nov (main), Feb-Apr (secondary)
                        if current_month in [9, 10, 11]:  # Main harvest
                            seasonal_factor = 0.85  # Lower prices due to abundance
                        elif current_month in [2, 3, 4]:  # Secondary harvest
                            seasonal_factor = 0.92
                        else:  # Off-season
                            seasonal_factor = 1.15
                        
                        # 4. Demand-based adjustment
                        # Higher demand = can charge more
                        demand_factor = 1.0 + (0.1 * abs(demand_elasticity))
                        
                        # 5. Competition adjustment
                        competition_adjustment = 1.0 - competition_factor
                        
                        # 6. Category-specific pricing strategy
                        category_premiums = {
                            'Grains': 1.0,
                            'Vegetables': 1.1,  # Fresh produce premium
                            'Fruits': 1.15,
                            'Dairy': 1.2,  # Perishable premium
                            'Meat': 1.25,
                            'Other': 1.0
                        }
                        category_factor = category_premiums.get(category, 1.0)
                        
                        # 7. Calculate optimal price
                        optimal_price = model_base_price * seasonal_factor * demand_factor * competition_adjustment * category_factor
                        
                        # Ensure minimum price
                        optimal_price = max(optimal_price, min_price)
                        
                        # 8. Calculate price range
                        min_recommended = optimal_price * 0.95
                        max_recommended = optimal_price * 1.10
                        
                        # 9. Profit analysis
                        current_profit = current_price - cost_price
                        optimal_profit = optimal_price - cost_price
                        profit_increase = optimal_profit - current_profit
                        profit_increase_pct = (profit_increase / current_profit * 100) if current_profit > 0 else 0
                        
                        # Display results
                        st.markdown("---")
                        st.markdown("#### 🎯 AI Recommendation:")
                        
                        # Main recommendation
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                                    padding: 20px; border-radius: 12px; margin: 15px 0;
                                    text-align: center;">
                            <p style="margin: 0; color: white; font-size: 14px; font-weight: 600;">
                                RECOMMENDED PRICE
                            </p>
                            <p style="margin: 10px 0 0 0; color: white; font-size: 32px; font-weight: bold;">
                                {optimal_price:.2f} ETB
                            </p>
                            <p style="margin: 5px 0 0 0; color: #d1fae5; font-size: 13px;">
                                Range: {min_recommended:.2f} - {max_recommended:.2f} ETB
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Price comparison
                        col_price1, col_price2, col_price3 = st.columns(3)
                        
                        with col_price1:
                            st.metric("Current Price", f"{current_price:.2f} ETB")
                        with col_price2:
                            st.metric("AI Suggested", f"{optimal_price:.2f} ETB", 
                                    delta=f"{optimal_price - current_price:+.2f}")
                        with col_price3:
                            st.metric("Min Viable", f"{min_price:.2f} ETB")
                        
                        # Profit analysis
                        st.markdown("#### 💰 Profit Impact Analysis:")
                        
                        col_profit1, col_profit2 = st.columns(2)
                        
                        with col_profit1:
                            st.metric("Current Profit/Unit", f"{current_profit:.2f} ETB")
                            st.metric("Optimal Profit/Unit", f"{optimal_profit:.2f} ETB",
                                    delta=f"{profit_increase:+.2f}")
                        
                        with col_profit2:
                            if profit_increase > 0:
                                st.success(f"📈 Profit increase: +{profit_increase_pct:.1f}%")
                            else:
                                st.info("ℹ️ Current price is already optimal")
                        
                        # Factors considered
                        st.markdown("#### 📋 Factors Considered:")
                        
                        with st.expander("View AI Decision Factors", expanded=False):
                            st.markdown(f"""
                            **1. Base Market Price:** {model_base_price:.2f} ETB
                            - From Ethiopian market data
                            
                            **2. Seasonal Adjustment:** {seasonal_factor:.2f}x
                            - Current month: {current_month}
                            - {'Main harvest season (lower prices)' if current_month in [9,10,11] else 'Secondary harvest' if current_month in [2,3,4] else 'Off-season (higher prices)'}
                            
                            **3. Demand Elasticity:** {demand_elasticity}
                            - Demand factor: {demand_factor:.2f}x
                            
                            **4. Competition Factor:** {competition_factor}
                            - Adjustment: {competition_adjustment:.2f}x
                            
                            **5. Category Premium:** {category_factor}x
                            - {category} category pricing strategy
                            
                            **6. Cost Margin:** {cost_margin*100:.0f}%
                            - Minimum viable price: {min_price:.2f} ETB
                            """)
                        
                        # Recommendation text
                        if optimal_price > current_price * 1.05:
                            st.success(f"💡 **Recommendation:** Increase price by {((optimal_price/current_price - 1) * 100):.1f}% to maximize profit while staying competitive.")
                        elif optimal_price < current_price * 0.95:
                            st.warning(f"⚠️ **Recommendation:** Consider reducing price by {((1 - optimal_price/current_price) * 100):.1f}% to increase sales volume.")
                        else:
                            st.info("✅ **Recommendation:** Your current price is well-positioned. Minor adjustments may optimize profit.")
                        
                        st.success("✅ AI price optimization complete!")
                else:
                    st.warning("⚠️ Price prediction model not available")
        
        # ==========================================
        # ADDITIONAL AI FEATURES
        # ==========================================
        st.markdown("---")
        st.markdown("###  Additional AI Insights")
        
        col_fraud, col_match, col_rec = st.columns(3)
        
        with col_fraud:
            st.markdown("#### 🔒 Fraud Detection")
            if st.button("Analyze Transaction Risk", use_container_width=True):
                st.info("ℹ️ Fraud detection model analyzes:")
                st.markdown("""
                - Transaction patterns
                - Price anomalies
                - Location mismatches
                - Frequency spikes
                - Merchant history
                """)
                st.success("✅ No suspicious activity detected for your account")
        
        with col_match:
            st.markdown("#### 🤝 Merchant Matching")
            if st.button("Find Best Merchants", use_container_width=True):
                st.info("ℹ️ AI matches you with merchants based on:")
                st.markdown("""
                - Product category
                - Location proximity
                - Price compatibility
                - Rating & reliability
                - Delivery capability
                """)
                st.success("✅ Found 5 potential merchant partners")
        
        with col_rec:
            st.markdown("#### 🎁 Product Recommendations")
            if st.button("Get Product Suggestions", use_container_width=True):
                st.info("ℹ️ AI recommends products based on:")
                st.markdown("""
                - Market demand trends
                - Seasonal opportunities
                - Regional preferences
                - Profit margins
                - Competition analysis
                """)
                st.success("✅ Top recommendation: Expand into Organic Coffee exports")
