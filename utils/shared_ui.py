import streamlit as st
from utils.theme import get_custom_css, get_role_colors
from utils.auth import logout_user, initialize_session_state

def render_custom_css():
    """Render custom CSS styling"""
    st.markdown(get_custom_css(), unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with navigation"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        return None
    
    user_info = st.session_state.user_info
    role = user_info['role']
    role_colors = get_role_colors(role)
    
    with st.sidebar:
        # User profile section
        st.markdown(f"""
        <div class="user-profile">
            <div class="user-avatar">{user_info['name'][0].upper()}</div>
            <div class="user-info">
                <div class="user-name">{user_info['name']}</div>
                <div class="user-role">{role.title()}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation based on role
        menu_items = get_menu_items(role)
        
        for item in menu_items:
            if st.button(
                item['label'],
                key=f"nav_{item['page']}",
                use_container_width=True,
                type="primary" if st.session_state.get('current_page') == item['page'] else "secondary"
            ):
                st.session_state.current_page = item['page']
                st.rerun()
        
        st.markdown("---")
        
        # Logout button with confirmation
        if st.session_state.get('logout_confirmation', False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes", key="confirm_logout", use_container_width=True):
                    logout_user()
            with col2:
                if st.button("No", key="cancel_logout", use_container_width=True):
                    st.session_state.logout_confirmation = False
                    st.rerun()
        else:
            if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
                st.session_state.logout_confirmation = True
                st.rerun()
    
    return role

def get_menu_items(role: str) -> list:
    """Get menu items based on user role"""
    menus = {
        'producer': [
            {'label': '📊 Dashboard', 'page': 'producer_dashboard'},
            {'label': '📦 Manage Inventory', 'page': 'producer_inventory'},
            {'label': '📈 Analytics', 'page': 'producer_analytics'},
            {'label': '🚚 Shipments', 'page': 'producer_shipments'},
        ],
        'merchant': [
            {'label': '📊 Dashboard', 'page': 'merchant_dashboard'},
            {'label': '🛒 Orders', 'page': 'merchant_orders'},
            {'label': '💰 Pricing', 'page': 'merchant_pricing'},
            {'label': '📊 Reports', 'page': 'merchant_reports'},
        ],
        'customer': [
            {'label': '🏠 Home', 'page': 'customer_home'},
            {'label': '🛍️ Shop', 'page': 'customer_shop'},
            {'label': '📦 My Orders', 'page': 'customer_orders'},
            {'label': '💳 Wallet', 'page': 'customer_wallet'},
        ],
        'admin': [
            {'label': '📊 Dashboard', 'page': 'admin_dashboard'},
            {'label': '👥 Users', 'page': 'admin_users'},
            {'label': '📈 Analytics', 'page': 'admin_analytics'},
            {'label': '⚙️ Settings', 'page': 'admin_settings'},
        ]
    }
    
    return menus.get(role, [])

def render_header(title: str, subtitle: str = ""):
    """Render page header"""
    if st.session_state.authenticated:
        user_info = st.session_state.user_info
        role_colors = get_role_colors(user_info['role'])
        
        st.markdown(f"""
        <div class="page-header">
            <h1 class="page-title">{title}</h1>
            {f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)

def render_loading_state(message: str = "Loading..."):
    """Render loading state"""
    with st.spinner(message):
        yield

def show_success_message(message: str):
    """Show success message with animation"""
    st.success(f"✅ {message}")

def show_error_message(message: str):
    """Show error message"""
    st.error(f"❌ {message}")

def show_warning_message(message: str):
    """Show warning message"""
    st.warning(f"⚠️ {message}")

def show_info_message(message: str):
    """Show info message"""
    st.info(f"ℹ️ {message}")

def render_card(title: str, content: str, icon: str = "📦", color: str = "#4CAF50"):
    """Render a styled card"""
    st.markdown(f"""
    <div class="info-card" style="border-left: 4px solid {color};">
        <div class="card-header">
            <span class="card-icon">{icon}</span>
            <h3 class="card-title">{title}</h3>
        </div>
        <div class="card-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, delta: str = "", delta_color: str = "green"):
    """Render a metric card"""
    col = st.columns(1)[0]
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-delta {delta_color}">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

def render_hamburger_menu():
    """Render hamburger menu button for mobile"""
    # This is already handled by sidebar, but can be enhanced for mobile
    pass
