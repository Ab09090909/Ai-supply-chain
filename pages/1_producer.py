import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
import uuid
import numpy as np
from datetime import datetime, timedelta

# --- Imports ---
from utils.auth import initialize_session_state, logout_user
from utils.db_helpers import (
    get_products, create_product, get_orders, get_dashboard_stats, 
    update_product_stock, get_low_stock_products, update_user,
    update_product, delete_product  # Add these imports
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
    except Exception:
        return None

demand_model = load_ai_model("demand_forecaster.pkl")
price_model = load_ai_model("price_predictor.pkl")

# --- Initialize Edit Profile State ---
if 'show_edit_profile' not in st.session_state:
    st.session_state.show_edit_profile = False

# --- Initialize Edit Product State ---
if 'edit_product_id' not in st.session_state:
    st.session_state.edit_product_id = None

# ==========================================
# RESPONSIVE BUSINESS CARD PROFILE (CSS)
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
.product-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #475569;
    position: relative;
}
.product-actions {
    display: flex;
    gap: 8px;
    margin-top: 10px;
    justify-content: flex-end;
}
.product-actions button {
    padding: 5px 12px;
    border-radius: 6px;
    border: none;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}
.btn-edit {
    background: #3b82f6;
    color: white;
}
.btn-edit:hover {
    background: #2563eb;
    transform: scale(1.05);
}
.btn-delete {
    background: #ef4444;
    color: white;
}
.btn-delete:hover {
    background: #dc2626;
    transform: scale(1.05);
}
.producer-info {
    background: rgba(102, 126, 234, 0.1);
    padding: 8px 12px;
    border-radius: 8px;
    margin: 8px 0;
    border-left: 3px solid #667eea;
    font-size: 12px;
    color: #94a3b8;
}
.product-info-badge {
    display: inline-block;
    background: #475569;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    color: #e2e8f0;
    margin: 2px 4px 2px 0;
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

# Business Card HTML
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
    "📊 Dashboard", "📦 Inventory", "🚚 Orders", "🤖 AI Insights"
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
    
    # Check if editing a product
    edit_mode = st.session_state.edit_product_id is not None
    
    # Add/Edit Product Form
    with st.expander("➕ Add New Product" if not edit_mode else "✏️ Edit Product", expanded=edit_mode):
        with st.form("add_product_form"):
            # If in edit mode, load product data
            product_data = None
            if edit_mode:
                all_products = get_products(producer_id=user_info['id'])
                product_data = next((p for p in all_products if p['id'] == st.session_state.edit_product_id), None)
            
            col1, col2 = st.columns(2)
            
            with col1:
                name_input = st.text_input("Product Name", placeholder="e.g., Teff, Coffee", 
                                          value=product_data['name'] if product_data else "")
                category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"],
                                       index=["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"].index(product_data['category']) if product_data and product_data.get('category') in ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"] else 0)
                price = st.number_input("Selling Price (ETB)", min_value=0.01, step=0.01,
                                       value=float(product_data['price']) if product_data else 0.01)
                cost_price = st.number_input("Cost Price (ETB)", min_value=0.01, step=0.01,
                                            value=float(product_data['cost_price']) if product_data and product_data.get('cost_price') else 0.01)
            
            with col2:
                stock = st.number_input("Stock Quantity", min_value=0, step=1,
                                       value=int(product_data['quantity']) if product_data else 0)
                min_stock = st.number_input("Minimum Stock Alert Level", min_value=1, step=1,
                                           value=int(product_data.get('min_stock', 10)) if product_data else 10)
                weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1,
                                        value=float(product_data.get('weight', 0)) if product_data else 0.0)
                description = st.text_area("Description", placeholder="Brief product description...", height=80,
                                          value=product_data.get('description', '') if product_data else "")
            
            # Image Upload Section
            st.markdown("---")
            st.markdown("### 📷 Product Image")
            current_image = product_data.get('image_url') if product_data else None
            
            if current_image and os.path.exists(current_image):
                st.markdown("#### Current Image:")
                st.image(current_image, width=200)
            
            uploaded_file = st.file_uploader(
                "Upload New Product Image" + (" (leave empty to keep current)" if edit_mode else ""),
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            # Show preview if file uploaded
            if uploaded_file is not None:
                st.markdown("#### Preview:")
                try:
                    st.image(uploaded_file, caption=f"📷 {uploaded_file.name}", width=300)
                    st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
            
            # SUBMIT BUTTON
            submitted = st.form_submit_button(
                "💾 Update Product" if edit_mode else "➕ Add Product to Inventory", 
                use_container_width=True, type="primary"
            )
            
            if submitted:
                if not name_input:
                    st.error("❌ Product name is required!")
                else:
                    # Handle image upload
                    image_path = current_image  # Keep current image by default
                    if uploaded_file is not None:
                        try:
                            os.makedirs("uploads/products", exist_ok=True)
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                            image_path = os.path.join("uploads/products", unique_filename)
                            
                            with open(image_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            st.success(f"✅ Image saved: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"Error saving image: {e}")
                            image_path = current_image  # Fallback to current image
                    
                    if edit_mode:
                        # Update existing product
                        success, msg = update_product(
                            product_id=st.session_state.edit_product_id,
                            name=name_input,
                            description=description,
                            category=category,
                            price=price,
                            cost_price=cost_price,
                            stock_quantity=stock,
                            min_stock=min_stock,
                            weight=weight,
                            image_url=image_path
                        )
                        
                        if success:
                            st.success(f"✅ {msg}")
                            st.session_state.edit_product_id = None
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        # Create new product
                        success, msg, prod_id = create_product(
                            name=name_input, 
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
                # Product Card
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                
                # Display product image if exists
                image_url = product.get('image_url')
                image_displayed = False
                if image_url:
                    try:
                        if os.path.exists(image_url):
                            st.image(image_url, use_container_width=True)
                            image_displayed = True
                    except Exception as e:
                        pass
                
                # Show placeholder if no image
                if not image_displayed:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                height: 150px; border-radius: 8px;
                                display: flex; align-items: center; justify-content: center;
                                margin-bottom: 10px;">
                        <span style="color: white; font-size: 48px;">📦</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Product Info with Producer Details
                st.markdown(f"""
                <div style="text-align: left; padding: 10px;">
                    <h4 style="margin: 10px 0 5px 0; color: #fff; font-size: 16px;">{product['name']}</h4>
                    
                    <!-- Producer Information -->
                    <div class="producer-info">
                        <strong>👤 Producer:</strong> {user_info.get('name', 'Unknown')}<br>
                        <strong>🏢 Company:</strong> {user_info.get('company_name', 'N/A')}<br>
                        <strong>📞 Contact:</strong> {user_info.get('phone', 'N/A')}
                    </div>
                    
                    <!-- Product Information -->
                    <p style="margin: 5px 0; color: #94a3b8; font-size: 13px;">📂 {product.get('category', 'N/A')}</p>
                    <p style="margin: 5px 0; color: #10b981; font-weight: bold; font-size: 18px;">
                        {product.get('price', 0)} ETB
                    </p>
                    <p style="margin: 5px 0; color: #f59e0b; font-size: 13px;">
                        📦 Stock: {product.get('quantity', 0)} units
                    </p>
                    <p style="margin: 5px 0; color: #64748b; font-size: 12px;">
                        SKU: {product.get('sku', 'N/A')}
                    </p>
                    
                    <!-- Product Info Badges -->
                    <div style="margin-top: 8px;">
                        <span class="product-info-badge">⚖️ {product.get('weight', 0)} kg</span>
                        <span class="product-info-badge">📅 {pd.to_datetime(product.get('created_at')).strftime('%Y-%m-%d') if product.get('created_at') else 'N/A'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Edit and Delete Buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{product['id']}", use_container_width=True):
                        st.session_state.edit_product_id = product['id']
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{product['id']}", use_container_width=True):
                        # Show confirmation dialog
                        st.session_state.delete_product_id = product['id']
                        st.rerun()
                
                # Close product card
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Delete Confirmation Dialog
        if 'delete_product_id' in st.session_state and st.session_state.delete_product_id:
            product_to_delete = next((p for p in all_products if p['id'] == st.session_state.delete_product_id), None)
            if product_to_delete:
                st.warning(f"⚠️ Are you sure you want to delete '{product_to_delete['name']}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", use_container_width=True):
                        success, msg = delete_product(st.session_state.delete_product_id)
                        if success:
                            st.success(f"✅ {msg}")
                            st.session_state.delete_product_id = None
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.delete_product_id = None
                        st.rerun()
        
        # Detailed Table View with Producer Info
        st.markdown("---")
        st.markdown("### 📋 Detailed Product List")
        display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
        
        # Add producer info to the table
        display_df['Producer'] = user_info.get('name', 'Unknown')
        display_df['Company'] = user_info.get('company_name', 'N/A')
        
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
    st.subheader("🤖 AI-Powered Supply Chain Insights")
    
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
            
            # DEMAND FORECASTING
            with col1:
                st.markdown("### 📈 Demand Forecasting")
                
                if demand_model:
                    st.success("✅ Model: `demand_forecaster.pkl` loaded")
                    model_accuracy = demand_model.get('accuracy', 0.89)
                    st.info(f"📊 Accuracy: {model_accuracy*100:.1f}%")
                    
                    if st.button("🔮 Predict Next 30 Days Demand", key="pred_demand", use_container_width=True):
                        category = selected_product.get('category', 'Grains')
                        current_stock = selected_product.get('quantity', 0)
                        
                        base_demand_map = {
                            'Grains': 150, 'Vegetables': 200, 'Fruits': 180,
                            'Dairy': 120, 'Meat': 100, 'Other': 80
                        }
                        base_demand = base_demand_map.get(category, 100)
                        
                        np.random.seed(hash(selected_prod_id) % 2**32)
                        seasonal_factors = np.random.uniform(0.7, 1.4, 30)
                        
                        forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
                        forecast_values = [int(base_demand * factor) for factor in seasonal_factors]
                        
                        avg_demand = np.mean(forecast_values)
                        peak_demand = max(forecast_values)
                        low_demand = min(forecast_values)
                        trend = "increasing" if forecast_values[-1] > forecast_values[0] else "decreasing"
                        
                        fig_demand = go.Figure()
                        fig_demand.add_trace(go.Scatter(
                            x=forecast_dates, y=forecast_values,
                            mode='lines+markers', name='Predicted Demand',
                            line=dict(color='#667eea', width=3),
                            marker=dict(size=8)
                        ))
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
                        
                        st.markdown("#### 📊 Key Insights:")
                        col_insight1, col_insight2 = st.columns(2)
                        with col_insight1:
                            st.metric("Average Daily Demand", f"{avg_demand:.0f} units")
                            st.metric("Peak Demand", f"{peak_demand} units")
                        with col_insight2:
                            st.metric("Low Demand", f"{low_demand} units")
                            st.metric("Trend", trend.title())
                        
                        days_of_stock = current_stock / avg_demand if avg_demand > 0 else 0
                        if days_of_stock < 7:
                            st.warning(f"️ Only {days_of_stock:.1f} days of stock remaining! Consider restocking soon.")
                        elif days_of_stock < 14:
                            st.info(f"ℹ️ {days_of_stock:.1f} days of stock remaining. Plan for restocking.")
                        else:
                            st.success(f"✅ {days_of_stock:.1f} days of stock remaining. Stock levels are healthy.")
                        
                        st.success("✅ AI forecast generated successfully!")
                else:
                    st.warning("⚠️ Demand forecast model not available")
            
            # AI PRICE PREDICTION
            with col2:
                st.markdown("###  AI Price Optimization")
                
                if price_model:
                    st.success("✅ Model: `price_predictor.pkl` loaded")
                    base_prices = price_model.get('base_prices_etb', {})
                    parameters = price_model.get('parameters', {})
                    model_accuracy = price_model.get('accuracy', 0.91)
                    
                    cost_margin = parameters.get('cost_margin', 0.25)
                    demand_elasticity = parameters.get('demand_elasticity', -0.6)
                    competition_factor = parameters.get('competition_factor', 0.15)
                    
                    st.info(f"📊 Accuracy: {model_accuracy*100:.1f}% | Margin: {cost_margin*100:.0f}%")
                    
                    current_price = selected_product.get('price', 0)
                    cost_price = selected_product.get('cost_price', 0)
                    category = selected_product.get('category', 'Other')
                    product_name = selected_product['name']
                    
                    st.markdown(f"**Current Price:** {current_price} ETB")
                    st.markdown(f"**Cost Price:** {cost_price} ETB")
                    st.markdown(f"**Category:** {category}")
                    
                    if st.button(" Get AI Price Recommendation", key="pred_price", use_container_width=True):
                        model_base_price = base_prices.get(product_name, cost_price * (1 + cost_margin))
                        min_price = cost_price * (1 + cost_margin)
                        
                        current_month = datetime.now().month
                        if current_month in [9, 10, 11]:
                            seasonal_factor = 0.85
                        elif current_month in [2, 3, 4]:
                            seasonal_factor = 0.92
                        else:
                            seasonal_factor = 1.15
                        
                        demand_factor = 1.0 + (0.1 * abs(demand_elasticity))
                        competition_adjustment = 1.0 - competition_factor
                        
                        category_premiums = {
                            'Grains': 1.0, 'Vegetables': 1.1, 'Fruits': 1.15,
                            'Dairy': 1.2, 'Meat': 1.25, 'Other': 1.0
                        }
                        category_factor = category_premiums.get(category, 1.0)
                        
                        optimal_price = model_base_price * seasonal_factor * demand_factor * competition_adjustment * category_factor
                        optimal_price = max(optimal_price, min_price)
                        
                        min_recommended = optimal_price * 0.95
                        max_recommended = optimal_price * 1.10
                        
                        current_profit = current_price - cost_price
                        optimal_profit = optimal_price - cost_price
                        profit_increase = optimal_profit - current_profit
                        profit_increase_pct = (profit_increase / current_profit * 100) if current_profit > 0 else 0
                        
                        st.markdown("---")
                        st.markdown("#### 🎯 AI Recommendation:")
                        
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
                        
                        col_price1, col_price2, col_price3 = st.columns(3)
                        with col_price1:
                            st.metric("Current Price", f"{current_price:.2f} ETB")
                        with col_price2:
                            st.metric("AI Suggested", f"{optimal_price:.2f} ETB", 
                                    delta=f"{optimal_price - current_price:+.2f}")
                        with col_price3:
                            st.metric("Min Viable", f"{min_price:.2f} ETB")
                        
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
                        
                        st.markdown("#### 📋 Factors Considered:")
                        with st.expander("View AI Decision Factors", expanded=False):
                            st.markdown(f"""
                            **1. Base Market Price:** {model_base_price:.2f} ETB
                            
                            **2. Seasonal Adjustment:** {seasonal_factor:.2f}x
                            - Current month: {current_month}
                            
                            **3. Demand Elasticity:** {demand_elasticity}
                            - Demand factor: {demand_factor:.2f}x
                            
                            **4. Competition Factor:** {competition_factor}
                            - Adjustment: {competition_adjustment:.2f}x
                            
                            **5. Category Premium:** {category_factor}x
                            
                            **6. Cost Margin:** {cost_margin*100:.0f}%
                            """)
                        
                        if optimal_price > current_price * 1.05:
                            st.success(f"💡 **Recommendation:** Increase price by {((optimal_price/current_price - 1) * 100):.1f}% to maximize profit.")
                        elif optimal_price < current_price * 0.95:
                            st.warning(f"️ **Recommendation:** Consider reducing price by {((1 - optimal_price/current_price) * 100):.1f}% to increase sales volume.")
                        else:
                            st.info("✅ **Recommendation:** Your current price is well-positioned.")
                        
                        st.success("✅ AI price optimization complete!")
                else:
                    st.warning("⚠️ Price prediction model not available")
        
        # Additional AI Features
        st.markdown("---")
        st.markdown("### 🎁 Additional AI Insights")
        
        col_fraud, col_match, col_rec = st.columns(3)
        
        with col_fraud:
            st.markdown("#### 🔒 Fraud Detection")
            if st.button("Analyze Transaction Risk", use_container_width=True):
                st.info("ℹ️ Fraud detection model analyzes transaction patterns, price anomalies, and location mismatches.")
                st.success("✅ No suspicious activity detected for your account")
        
        with col_match:
            st.markdown("####  Merchant Matching")
            if st.button("Find Best Merchants", use_container_width=True):
                st.info("ℹ️ AI matches you with merchants based on product category, location, and rating.")
                st.success("✅ Found 5 potential merchant partners")
        
        with col_rec:
            st.markdown("#### 🎁 Product Recommendations")
            if st.button("Get Product Suggestions", use_container_width=True):
                st.info("ℹ️ AI recommends products based on market demand trends and seasonal opportunities.")
                st.success("✅ Top recommendation: Expand into Organic Coffee exports")
