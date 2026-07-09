import streamlit as st
from utils.auth import (
    initialize_session_state, 
    login_user, 
    register_user, 
    forgot_password,
    reset_password
)
from utils.shared_ui import render_custom_css, render_sidebar
from utils.theme import get_role_colors
import time

# Page configuration
st.set_page_config(
    page_title="AI Supply Chain",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Render custom CSS
render_custom_css()

def render_login_page():
    """Render the login page with enhanced validation and UX"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="login-header">
            <h1>🚀 AI Supply Chain</h1>
            <p>Intelligent Supply Chain Management Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login tabs
        tab_login, tab_signup, tab_forgot = st.tabs(["🔐 Login", "📝 Sign Up", "🔑 Forgot Password"])
        
        with tab_login:
            render_login_form()
        
        with tab_signup:
            render_signup_form()
        
        with tab_forgot:
            render_forgot_password_form()
    
    with col2:
        st.markdown("""
        <div class="login-features">
            <h2>Why Choose Us?</h2>
            <div class="feature">
                <div class="feature-icon">🤖</div>
                <div class="feature-text">
                    <h3>AI-Powered Insights</h3>
                    <p>Get intelligent predictions and recommendations</p>
                </div>
            </div>
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <div class="feature-text">
                    <h3>Real-time Tracking</h3>
                    <p>Monitor your supply chain in real-time</p>
                </div>
            </div>
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <div class="feature-text">
                    <h3>Secure & Reliable</h3>
                    <p>Enterprise-grade security and reliability</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_login_form():
    """Render login form with validation"""
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email Address", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        remember_me = st.checkbox("Remember me", value=False)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
        with col2:
            st.form_submit_button("🔄 Reset", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
                return
            
            # Show loading state
            with st.spinner("Authenticating..."):
                time.sleep(0.5)  # Simulate network delay
                success, message, user_info = login_user(email, password, remember_me)
                
                if success:
                    st.success(message)
                    time.sleep(0.5)
                    st.session_state.current_page = f"{user_info['role']}_dashboard"
                    st.rerun()
                else:
                    st.error(message)

def render_signup_form():
    """Render signup form with validation"""
    with st.form("signup_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your@email.com")
        with col2:
            password = st.text_input("Password", type="password", placeholder="Min 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        role = st.selectbox(
            "I am a:",
            ["producer", "merchant", "customer", "admin"],
            format_func=lambda x: x.title()
        )
        
        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submit:
            # Validation
            if not name or not email or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            # Show loading state
            with st.spinner("Creating account..."):
                time.sleep(0.5)
                success, message = register_user(name, email, password, role)
                
                if success:
                    st.success(message)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)

def render_forgot_password_form():
    """Render forgot password form"""
    with st.form("forgot_password_form", clear_on_submit=False):
        email = st.text_input("Email Address", placeholder="Enter your registered email")
        submit = st.form_submit_button("Send Reset Link", use_container_width=True, type="primary")
        
        if submit:
            if not email:
                st.error("Please enter your email")
                return
            
            with st.spinner("Processing..."):
                time.sleep(0.5)
                success, message = forgot_password(email)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Password reset section (shown when token is provided)
        st.markdown("---")
        st.markdown("### Reset Password")
        
        col1, col2 = st.columns(2)
        with col1:
            reset_email = st.text_input("Email", key="reset_email")
        with col2:
            reset_token = st.text_input("Reset Token", key="reset_token")
        
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")
        
        reset_submit = st.button("Reset Password", use_container_width=True, type="secondary")
        
        if reset_submit:
            if not reset_email or not reset_token or not new_password:
                st.error("Please fill in all fields")
                return
            
            if new_password != confirm_new_password:
                st.error("Passwords do not match")
                return
            
            with st.spinner("Resetting password..."):
                time.sleep(0.5)
                success, message = reset_password(reset_email, reset_token, new_password)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)

def render_dashboard():
    """Render main dashboard based on user role"""
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Render sidebar navigation
    role = render_sidebar()
    
    if role:
        role_colors = get_role_colors(role)
        user_info = st.session_state.user_info
        
        # Welcome message
        st.markdown(f"""
        <div class="welcome-banner" style="background: linear-gradient(135deg, {role_colors['primary']}22, {role_colors['secondary']}22);">
            <h1>Welcome back, {user_info['name']}! 👋</h1>
            <p>Here's what's happening with your supply chain today.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Orders", "24", "+12%")
        with col2:
            st.metric("Revenue", "$12.5K", "+8%")
        with col3:
            st.metric("Pending Shipments", "7", "-3%")
        with col4:
            st.metric("Customer Satisfaction", "98%", "+2%")
        
        st.markdown("---")
        
        # Role-specific content
        if role == 'producer':
            render_producer_dashboard()
        elif role == 'merchant':
            render_merchant_dashboard()
        elif role == 'customer':
            render_customer_dashboard()
        elif role == 'admin':
            render_admin_dashboard()

def render_producer_dashboard():
    """Render producer-specific dashboard"""
    st.header("Producer Dashboard")
    st.write("Manage your production and inventory")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📦 Total Products: 156")
    with col2:
        st.info("🏭 Production Capacity: 85%")

def render_merchant_dashboard():
    """Render merchant-specific dashboard"""
    st.header("Merchant Dashboard")
    st.write("Manage your orders and pricing")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🛒 Active Orders: 42")
    with col2:
        st.info("💰 Monthly Revenue: $8,450")

def render_customer_dashboard():
    """Render customer-specific dashboard"""
    st.header("Customer Dashboard")
    st.write("Track your orders and manage purchases")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📦 Active Orders: 3")
    with col2:
        st.info("💳 Wallet Balance: $250")

def render_admin_dashboard():
    """Render admin-specific dashboard"""
    st.header("Admin Dashboard")
    st.write("System overview and management")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("👥 Total Users: 1,247")
    with col2:
        st.info("📊 System Health: 99.9%")
    with col3:
        st.info("🔔 Alerts: 2")

# Main application
if __name__ == "__main__":
    render_dashboard()
