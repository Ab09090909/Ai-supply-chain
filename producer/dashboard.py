import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from utils.auth import initialize_session_state, logout_user
from utils.db_helpers import (
    get_products, create_product, get_orders, get_dashboard_stats,
    update_product, delete_product, get_low_stock_products
)

# Initialize
initialize_session_state()

# Auth Guard
if not st.session_state.authenticated:
    st.error("🔒 Please log in to access this page.")
    st.stop()

if st.session_state.user_info['role'] != 'producer':
    st.error(" Access Denied. This page is for Producers only.")
    st.stop()

user_info = st.session_state.user_info

# ==========================================
# MODERN CSS STYLING
# ==========================================
st.markdown("""
<style>
/* Main container */
.main > div {
    padding: 0 !important;
    background: #f8fafc;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Modern card design */
.modern-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}

.modern-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}

/* Profile section */
.profile-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    color: white;
}

.profile-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.profile-name {
    font-size: 24px;
    font-weight: 700;
    margin: 0;
}

.profile-role {
    font-size: 14px;
    opacity: 0.9;
    margin: 4px 0 0 0;
}

/* Status badges */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 4px 0;
}

.status-active {
    background: #dcfce7;
    color: #166534;
}

.status-inactive {
    background: #fee2e2;
    color: #991b1b;
}

/* Product card */
.product-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}

.product-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.product-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 48px;
}

.product-info {
    padding: 16px;
}

.product-title {
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: #1e293b;
}

.product-price {
    font-size: 24px;
    font-weight: 700;
    color: #16a34a;
    margin: 8px 0;
}

.product-meta {
    display: flex;
    gap: 12px;
    margin: 12px 0;
    font-size: 13px;
    color: #64748b;
}

.product-meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Stats cards */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin: 20px 0;
}

.stat-card {
    background: white;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-value {
    font-size: 28px;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
}

.stat-label {
    font-size: 12px;
    color: #64748b;
    margin: 4px 0 0 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Bottom navigation */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #e2e8f0;
    padding: 12px 0;
    display: flex;
    justify-content: space-around;
    z-index: 1000;
}

.nav-item {
    flex: 1;
    text-align: center;
    padding: 8px;
    cursor: pointer;
    border-radius: 12px;
    transition: all 0.2s;
}

.nav-item:hover {
    background: #f1f5f9;
}

.nav-item.active {
    background: #667eea;
    color: white;
}

.nav-icon {
    font-size: 24px;
    margin-bottom: 4px;
}

.nav-label {
    font-size: 11px;
    font-weight: 600;
}

/* Section title */
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #1e293b;
    margin: 24px 0 16px 0;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
}

.stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-2px);
}

/* Hide Streamlit menu */
.stApp [data-testid="stToolbar"] {
    display: none;
}

/* Responsive */
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .product-meta {
        flex-direction: column;
        gap: 8px;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE FOR NAVIGATION
# ==========================================
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'dashboard'

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def render_profile_header():
    """Render modern profile header"""
    name = user_info.get('name', 'Producer')
    initial = name[0].upper()
    company = user_info.get('company_name', 'Independent Producer')
    region = user_info.get('region', 'Addis Ababa')
    
    st.markdown(f"""
    <div class="profile-header">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div class="profile-avatar">{initial}</div>
            <div style="flex: 1;">
                <h1 class="profile-name">{name}</h1>
                <p class="profile-role">{company}</p>
                <p class="profile-role" style="margin-top: 4px;"> {region}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_stats():
    """Render statistics cards"""
    stats = get_dashboard_stats('producer', user_info['id'])
    
    st.markdown("""
    <div class="stats-grid">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value">{stats.get('total_products', 0)}</p>
            <p class="stat-label">Total Products</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value">{stats.get('low_stock', 0)}</p>
            <p class="stat-label">Low Stock</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value">{stats.get('total_orders', 0)}</p>
            <p class="stat-label">Total Orders</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-value">{stats.get('revenue', 0):,.0f}</p>
            <p class="stat-label">Revenue (ETB)</p>
        </div>
        """, unsafe_allow_html=True)

def render_product_card(product):
    """Render a single product card"""
    product_name = product.get('name', 'Unknown')
    price = product.get('price', 0)
    stock = product.get('quantity', 0)
    category = product.get('category', 'Other')
    is_available = product.get('is_active', True)
    image_b64 = product.get('image_base64')
    
    status_class = "status-active" if is_available else "status-inactive"
    status_text = "Active" if is_available else "Inactive"
    
    # Image display
    if image_b64:
        try:
            img_html = f'<div class="product-image" style="background: none;"><img src="data:image/jpeg;base64,{image_b64}" style="width:100%;height:100%;object-fit:cover;"></div>'
        except:
            img_html = f'<div class="product-image">📦</div>'
    else:
        img_html = f'<div class="product-image">📦</div>'
    
    st.markdown(f"""
    <div class="product-card">
        {img_html}
        <div class="product-info">
            <h3 class="product-title">{product_name}</h3>
            <span class="status-badge {status_class}">{status_text}</span>
            <p style="color: #64748b; font-size: 13px; margin: 8px 0;"> {category}</p>
            <p class="product-price">{price:,.2f} ETB</p>
            <div class="product-meta">
                <div class="product-meta-item"> {stock} units</div>
                <div class="product-meta-item">⚖️ {product.get('weight', 0)} kg</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard_tab():
    """Render Dashboard tab"""
    render_profile_header()
    render_stats()
    
    st.markdown('<h2 class="section-title">Recent Products</h2>', unsafe_allow_html=True)
    
    products = get_products(producer_id=user_info['id'], limit=6)
    
    if products:
        for product in products:
            render_product_card(product)
    else:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 40px;">
            <p style="font-size: 48px; margin: 0;">📦</p>
            <p style="color: #64748b; margin: 16px 0;">No products yet</p>
            <p style="color: #94a3b8; font-size: 14px;">Add your first product to get started</p>
        </div>
        """, unsafe_allow_html=True)

def render_products_tab():
    """Render Products tab"""
    st.markdown('<h2 class="section-title">My Products</h2>', unsafe_allow_html=True)
    
    # Add new product button
    if st.button("➕ Add New Product", use_container_width=True, type="primary"):
        st.session_state.show_add_product = True
    
    # Add product form
    if st.session_state.get('show_add_product', False):
        with st.form("add_product_form", clear_on_submit=True):
            st.markdown("### Add New Product")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name *")
                category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"])
                price = st.number_input("Price (ETB)", min_value=0.01, step=0.01)
                cost = st.number_input("Cost Price (ETB)", min_value=0.01, step=0.01)
            
            with col2:
                stock = st.number_input("Stock Quantity", min_value=0, step=1)
                weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
                min_stock = st.number_input("Min Stock Level", min_value=1, value=10)
                description = st.text_area("Description", height=80)
            
            uploaded_image = st.file_uploader("Product Image", type=['jpg', 'jpeg', 'png'])
            
            image_b64 = None
            if uploaded_image:
                image_b64 = base64.b64encode(uploaded_image.read()).decode()
                st.image(uploaded_image, width=150)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Save Product", type="primary", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)
            
            if submitted:
                if name:
                    success, msg, _ = create_product(
                        name=name, description=description, category=category,
                        price=price, cost_price=cost, stock_quantity=stock,
                        producer_id=user_info['id'], weight=weight,
                        image_base64=image_b64
                    )
                    if success:
                        st.success(msg)
                        st.session_state.show_add_product = False
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Product name is required!")
            
            if cancelled:
                st.session_state.show_add_product = False
                st.rerun()
        
        st.markdown("---")
    
    # Display all products
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        for product in all_products:
            render_product_card(product)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✏️ Edit", key=f"edit_{product['id']}", use_container_width=True):
                    st.session_state.edit_product_id = product['id']
            with col2:
                if st.button("🗑️ Delete", key=f"del_{product['id']}", use_container_width=True):
                    if delete_product(product['id']):
                        st.success("Product deleted")
                        st.rerun()
            with col3:
                status = "Deactivate" if product.get('is_active', True) else "Activate"
                if st.button(status, key=f"act_{product['id']}", use_container_width=True):
                    new_status = not product.get('is_active', True)
                    update_product(product['id'], is_active=new_status)
                    st.rerun()
    else:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 40px;">
            <p style="font-size: 48px; margin: 0;">📦</p>
            <p style="color: #64748b; margin: 16px 0;">No products found</p>
        </div>
        """, unsafe_allow_html=True)

def render_orders_tab():
    """Render Orders tab"""
    st.markdown('<h2 class="section-title">Orders</h2>', unsafe_allow_html=True)
    
    orders = get_orders(user_info['id'], 'producer', limit=20)
    
    if orders:
        for order in orders:
            status = order.get('status', 'pending')
            status_class = {
                'pending': 'status-inactive',
                'confirmed': 'status-active',
                'delivered': 'status-active'
            }.get(status, 'status-inactive')
            
            st.markdown(f"""
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span class="status-badge {status_class}">{status.upper()}</span>
                    <span style="color: #64748b; font-size: 12px;">{order.get('created_at', '')[:10]}</span>
                </div>
                <p style="font-weight: 700; margin: 8px 0;">Order #{str(order.get('id', ''))[:8]}</p>
                <p style="color: #64748b; font-size: 14px; margin: 4px 0;">Quantity: {order.get('quantity', 0)} units</p>
                <p style="color: #16a34a; font-weight: 700; font-size: 18px; margin: 8px 0;">{order.get('total_amount', 0):,.2f} ETB</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 40px;">
            <p style="font-size: 48px; margin: 0;">📬</p>
            <p style="color: #64748b; margin: 16px 0;">No orders yet</p>
        </div>
        """, unsafe_allow_html=True)

def render_profile_tab():
    """Render Profile tab"""
    render_profile_header()
    
    st.markdown('<h2 class="section-title">Account Information</h2>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="modern-card">
        <p style="margin: 8px 0;"><strong>Name:</strong> {user_info.get('name', 'N/A')}</p>
        <p style="margin: 8px 0;"><strong>Email:</strong> {user_info.get('email', 'N/A')}</p>
        <p style="margin: 8px 0;"><strong>Phone:</strong> {user_info.get('phone', 'N/A')}</p>
        <p style="margin: 8px 0;"><strong>Company:</strong> {user_info.get('company_name', 'N/A')}</p>
        <p style="margin: 8px 0;"><strong>Region:</strong> {user_info.get('region', 'N/A')}</p>
        <p style="margin: 8px 0;"><strong>Role:</strong> Producer</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout_user()

# ==========================================
# BOTTOM NAVIGATION
# ==========================================
def render_bottom_nav():
    """Render bottom navigation bar"""
    tabs = [
        ('dashboard', '📊', 'Dashboard'),
        ('products', '📦', 'Products'),
        ('orders', '📬', 'Orders'),
        ('profile', '👤', 'Profile')
    ]
    
    st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)
    
    cols = st.columns(len(tabs))
    
    for idx, (tab_id, icon, label) in enumerate(tabs):
        with cols[idx]:
            is_active = st.session_state.current_tab == tab_id
            class_name = "nav-item active" if is_active else "nav-item"
            
            if st.button(f"{icon}<br>{label}", key=f"nav_{tab_id}", 
                        use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.current_tab = tab_id
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MAIN APP
# ==========================================
# Main content area with padding for bottom nav
st.markdown('<div style="padding-bottom: 100px;">', unsafe_allow_html=True)

# Render current tab
if st.session_state.current_tab == 'dashboard':
    render_dashboard_tab()
elif st.session_state.current_tab == 'products':
    render_products_tab()
elif st.session_state.current_tab == 'orders':
    render_orders_tab()
elif st.session_state.current_tab == 'profile':
    render_profile_tab()

st.markdown('</div>', unsafe_allow_html=True)

# Bottom navigation
render_bottom_nav()
