import streamlit as st

# Set page config FIRST
st.set_page_config(
    page_title="PlyChain - AI Supply Chain",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None

# ==========================================
# MODERN CSS STYLING
# ==========================================
st.markdown("""
<style>
/* Global Styles */
.stApp {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}

/* Welcome Hero Section */
.welcome-hero {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 20px;
    padding: 40px 20px;
    margin-bottom: 30px;
    border: 1px solid #334155;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* Feature Cards */
.feature-card {
    background: #1e293b;
    border-radius: 16px;
    padding: 25px 20px;
    border: 1px solid #334155;
    height: 100%;
    text-align: center;
    transition: all 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-5px);
    border-color: #667eea;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
}
.feature-icon {
    font-size: 40px;
    margin-bottom: 15px;
}

/* CTA Button */
.cta-container {
    text-align: center;
    margin-top: 40px;
    margin-bottom: 20px;
}

/* Login/Signup Form Styling */
[data-testid="stForm"] {
    background: #1e293b;
    padding: 30px;
    border-radius: 16px;
    border: 1px solid #334155;
}

@media (max-width: 768px) {
    .welcome-hero { padding: 30px 15px; }
    .feature-card { margin-bottom: 15px; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# AUTHENTICATION FLOW
# ==========================================
if not st.session_state.authenticated:
    st.markdown('<div class="welcome-hero"><h1 style="color: #f8fafc; margin-bottom: 10px;"> PlyChain</h1><p style="color: #94a3b8; font-size: 16px;">Intelligent Supply Chain Management for Ethiopia</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([" Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if email and password:
                    try:
                        from utils.auth import login_user
                        success, msg, user = login_user(email, password)
                        if success:
                            st.success(msg)
                            st.session_state.authenticated = True
                            st.session_state.user_info = user
                            st.rerun()
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("I am a:", ["producer", "merchant", "customer", "admin"])
            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit:
                if name and email and password:
                    try:
                        from utils.auth import register_user
                        success, msg = register_user(name, email, password, role)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"Registration error: {str(e)}")
                else:
                    st.error("Please fill in all fields")

# ==========================================
# POST-LOGIN WELCOME SCREEN
# ==========================================
else:
    user_info = st.session_state.user_info
    name = user_info.get('name', 'there')
    role = user_info.get('role', 'user').capitalize()
    
    # 1. Welcome Hero
    st.markdown(f"""
    <div class="welcome-hero">
        <h1 style="color: #f8fafc; margin-bottom: 10px;">Welcome back, {name}! 👋</h1>
        <p style="color: #94a3b8; font-size: 18px;">You are logged in as <strong style="color: #667eea;">{role}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. System Overview
    st.subheader(" About PlyChain System")
    st.markdown("""
    <p style="color: #cbd5e1; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
        PlyChain is an AI-powered supply chain platform designed specifically for the Ethiopian market. 
        We connect producers, merchants, and customers through intelligent matching, real-time market insights, 
        and secure transaction management. Our system uses advanced machine learning to predict demand, 
        optimize pricing, and ensure fair trade across all regions.
    </p>
    """, unsafe_allow_html=True)
    
    # 3. Feature Highlights
    st.subheader("🚀 Key Features")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h4 style="color: #f8fafc; margin-bottom: 10px;">AI Insights</h4>
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">Smart demand forecasting and price optimization based on real Ethiopian market data.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤝</div>
            <h4 style="color: #f8fafc; margin-bottom: 10px;">Smart Matching</h4>
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">Automatically connects producers with the best merchants based on location and needs.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h4 style="color: #f8fafc; margin-bottom: 10px;">Real-Time Tracking</h4>
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">Monitor inventory, orders, and revenue with beautiful, interactive dashboards.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <h4 style="color: #f8fafc; margin-bottom: 10px;">Secure & Verified</h4>
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">Fraud detection and verified user profiles ensure safe and trustworthy transactions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 4. Call to Action & Navigation
    st.markdown('<div class="cta-container">', unsafe_allow_html=True)
    st.markdown(f"### Ready to manage your {role.lower()} dashboard?")
    
    # Role-based navigation buttons
    if st.button(f"🚀 Go to {role} Dashboard", use_container_width=True, type="primary"):
        if role == 'Producer':
            st.switch_page("pages/1_producer.py")
        elif role == 'Merchant':
            st.switch_page("pages/2_merchant.py")
        elif role == 'Customer':
            st.switch_page("pages/3_customer.py")
        elif role == 'Admin':
            st.switch_page("pages/4_Admin.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Logout button at the bottom
    col_left, col_right, col_logout = st.columns([1, 1, 1])
    with col_logout:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()
