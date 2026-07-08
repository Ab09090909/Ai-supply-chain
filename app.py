"""
app.py — Ethiopian AI Supply Chain Platform (Main Entry)
"""
import sys
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────
try:
    from utils.theme import inject_theme, render_theme_toggle
    from utils.auth import sign_in, sign_up, sign_out, forgot_password
    from utils.constants import REGIONS
    from utils.db_helpers import supabase, cached_get_profile, clear_data_cache
    from utils.verification import check_verification_status
except ImportError as e:
    st.error(f"⚠️ Import error: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "profile" not in st.session_state:
    st.session_state.profile = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "auth_redirect" not in st.session_state:
    st.session_state.auth_redirect = False
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# Inject theme
inject_theme()

# ─────────────────────────────────────────────────────────────
# CSS - HIDE SIDEBAR, SHOW HAMBURGER MENU
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── HIDE DEFAULT STREAMLIT SIDEBAR ─── */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="stSidebarContent"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ─── HIDE STREAMLIT BRANDING ─── */
#MainMenu, footer, header {
    visibility: hidden !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}

/* ─── HAMBURGER MENU BUTTON ─── */
.hamburger-btn {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 999997;
    background: #1B4332;
    color: white;
    border: 2px solid #2D6A4F;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.hamburger-btn:hover {
    background: #2D6A4F;
}

/* ─── SIDEBAR OVERLAY ─── */
.mobile-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    z-index: 999998;
}
.mobile-overlay.active {
    display: block;
}

/* ─── CUSTOM SIDEBAR ─── */
.mobile-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 280px;
    height: 100%;
    background: #161b27;
    z-index: 999999;
    padding: 20px;
    overflow-y: auto;
    border-right: 1px solid #1e2a3a;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
}
.mobile-sidebar.open {
    transform: translateX(0);
}

/* ─── CLOSE BUTTON ─── */
.close-sidebar-btn {
    background: transparent;
    border: none;
    color: #e2e8f0;
    font-size: 24px;
    cursor: pointer;
    float: right;
    padding: 5px 10px;
}
.close-sidebar-btn:hover {
    color: #f87171;
}

/* ─── SIDEBAR PROFILE ─── */
.sidebar-profile {
    text-align: center;
    margin: 10px 0 20px 0;
}
.sidebar-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #1e2a3a;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    font-size: 24px;
    color: #f1f5f9;
    font-weight: 700;
    border: 2px solid #D4A017;
}
.sidebar-name {
    font-size: 16px;
    font-weight: 600;
    margin-top: 8px;
    color: #e2e8f0;
}
.sidebar-role {
    font-size: 12px;
    color: #94a3b8;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid #1e2a3a;
    margin: 12px 0;
}

/* ─── SIDEBAR NAVIGATION BUTTONS ─── */
.sidebar-nav-btn {
    width: 100%;
    padding: 10px 14px;
    margin-bottom: 4px;
    background: #1e2a3a;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s;
}
.sidebar-nav-btn:hover {
    border-color: #D4A017;
    color: #D4A017;
}

.sidebar-nav-btn-logout {
    width: 100%;
    padding: 10px 14px;
    margin-bottom: 4px;
    background: #7f1d1d44;
    border: 1px solid #ef444455;
    border-radius: 8px;
    color: #f87171;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s;
}
.sidebar-nav-btn-logout:hover {
    background: #7f1d1d66;
    border-color: #ef4444;
}

.sidebar-section-title {
    font-weight: 600;
    color: #94a3b8;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    margin-top: 12px;
}

/* ─── PILL STYLES ─── */
.pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.3px;
    margin: 2px 0;
}
.pill-success { background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }
.pill-warning { background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }
.pill-danger { background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }
.pill-info { background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }
.pill-neutral { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

/* ─── MAIN CONTENT ─── */
[data-testid="stAppViewBlockContainer"] {
    padding-top: 70px !important;
    padding-left: 16px !important;
    padding-right: 16px !important;
}

/* ─── BUTTONS ─── */
.stButton > button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    background: #1e2a3a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    border-color: #D4A01755 !important;
    color: #D4A017 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #D4A017 0%, #F4C430 100%) !important;
    border-color: #D4A017 !important;
    color: #1B4332 !important;
}

/* ─── INPUTS ─── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

/* ─── TABS ─── */
[data-testid="stTabs"] > div > div > div > button {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748b !important;
    padding: 8px 16px !important;
}
[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
    color: #D4A017 !important;
    border-bottom: 2px solid #D4A017 !important;
}

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 70px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
    [data-testid="stTabs"] > div > div > div > button {
        font-size: 12px !important;
        padding: 6px 10px !important;
        white-space: nowrap !important;
    }
    [data-testid="stTabs"] > div > div {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }
    div.stButton > button {
        width: 100% !important;
    }
}

@media (min-width: 769px) {
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 80px !important;
        padding-left: 24px !important;
        padding-right: 24px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HAMBURGER MENU BUTTON - Using Streamlit Button
# ─────────────────────────────────────────────────────────────
def render_hamburger_button():
    """Render the hamburger menu button using Streamlit."""
    # Use a Streamlit button in a fixed position container
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        if st.button("☰", key="hamburger_btn", help="Toggle Menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

# ─────────────────────────────────────────────────────────────
# CUSTOM SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_custom_sidebar(profile=None):
    """Render custom sidebar with hamburger menu."""
    
    # Get profile if not provided
    if profile is None:
        profile = st.session_state.get("profile")
    
    # Determine if menu should be open
    is_open = st.session_state.get("menu_open", False)
    overlay_class = "active" if is_open else ""
    
    if not profile or st.session_state.user is None:
        sidebar_html = f'''
        <div class="mobile-sidebar {'open' if is_open else ''}" id="mobileSidebar">
            <button class="close-sidebar-btn" onclick="document.getElementById('mobileSidebar').classList.remove('open'); document.getElementById('mobileOverlay').classList.remove('active');">✕</button>
            <div class="sidebar-profile">
                <div class="sidebar-avatar">🔐</div>
                <div class="sidebar-name">Not Signed In</div>
                <div class="sidebar-role">Please sign in</div>
            </div>
            <hr class="sidebar-divider">
            <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
        </div>
        <div class="mobile-overlay {overlay_class}" id="mobileOverlay" onclick="document.getElementById('mobileSidebar').classList.remove('open'); this.classList.remove('active');"></div>
        '''
        st.markdown(sidebar_html, unsafe_allow_html=True)
        return
    
    name = profile.get("full_name", "User")
    role = profile.get("role", "customer")
    region = profile.get("region", "N/A")
    role_icon = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}.get(role, "👤")
    
    sidebar_html = f'''
    <div class="mobile-sidebar {'open' if is_open else ''}" id="mobileSidebar">
        <button class="close-sidebar-btn" onclick="document.getElementById('mobileSidebar').classList.remove('open'); document.getElementById('mobileOverlay').classList.remove('active');">✕</button>
        
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{name[0].upper()}</div>
            <div class="sidebar-name">{name}</div>
            <div class="sidebar-role">{role_icon} {role.capitalize()} · {region}</div>
        </div>
        
        <hr class="sidebar-divider">
        
        <div class="sidebar-section-title">📊 Navigation</div>
        <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
    '''
    
    # Role-specific pages
    nav_pages = {
        "producer": ("🚜 Producer", "pages/1_producer.py"),
        "merchant": ("🏬 Merchant", "pages/2_merchant.py"),
        "customer": ("🛒 Customer", "pages/3_customer.py"),
        "admin": ("🛡️ Admin", "pages/4_Admin.py")
    }
    
    if role in nav_pages:
        label, page = nav_pages[role]
        sidebar_html += f'<button class="sidebar-nav-btn" onclick="window.location.href=\'{page}\'">{label}</button>'
    
    # Verification status
    try:
        verif_status = check_verification_status(st.session_state.user.id)
        if verif_status.get("is_verified", False):
            status_html = '<span class="pill pill-success">✅ Verified</span>'
        elif verif_status.get("has_documents", False):
            status_html = '<span class="pill pill-warning">⏳ Pending</span>'
        else:
            status_html = '<span class="pill pill-info">📄 Verify</span>'
    except Exception:
        status_html = '<span class="pill pill-neutral">⚠️ Unknown</span>'
    
    sidebar_html += f'''
        <hr class="sidebar-divider">
        <div class="sidebar-section-title">📌 Status</div>
        <div style="margin-bottom: 8px;">{status_html}</div>
        <hr class="sidebar-divider">
        <button class="sidebar-nav-btn-logout" onclick="document.getElementById('logoutForm').submit();">🚪 Log Out</button>
    </div>
    <div class="mobile-overlay {overlay_class}" id="mobileOverlay" onclick="document.getElementById('mobileSidebar').classList.remove('open'); this.classList.remove('active');"></div>
    '''
    
    st.markdown(sidebar_html, unsafe_allow_html=True)
    
    # Logout form
    st.markdown('''
    <form id="logoutForm" method="post" action="">
        <input type="hidden" name="logout" value="true">
    </form>
    ''', unsafe_allow_html=True)
    
    if st.query_params.get("logout") == "true":
        try:
            sign_out()
            st.session_state.user = None
            st.session_state.profile = None
            st.session_state.authenticated = False
            st.session_state.user_role = None
            clear_data_cache()
            st.query_params.clear()
            st.rerun()
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────────────────────
def show_landing():
    """Show login/register page."""
    
    # Hero
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%); 
                border-radius: 16px; padding: 30px 20px; text-align: center; color: white; margin-bottom: 20px;">
        <h1 style="font-size: 28px; margin: 0; color: white;">🌾 Ethiopian AI Supply Chain</h1>
        <p style="font-size: 14px; opacity: 0.9; margin-top: 8px;">
            AI-powered matching, price intelligence, and fraud detection
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Register"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if not email or not password:
                st.warning("Please enter email and password.")
            else:
                with st.spinner("Signing in..."):
                    ok, msg = sign_in(email, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.auth_redirect = True
                    st.rerun()
                else:
                    st.error(msg)
        
        with st.expander("🔑 Forgot Password?"):
            reset_email = st.text_input("Enter your email", key="reset_email")
            if st.button("📧 Send Reset Link", key="reset_btn", use_container_width=True):
                if not reset_email:
                    st.warning("Please enter your email address.")
                else:
                    with st.spinner("Sending..."):
                        ok, msg = forgot_password(reset_email)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
    
    with tab2:
        name = st.text_input("Full Name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("I am a...", ["producer", "merchant", "customer"])
        with col2:
            region = st.selectbox("Region", REGIONS)
        
        phone = st.text_input("Phone (optional)", key="reg_phone")
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if not all([name, email, password]):
                st.warning("Name, email, and password are required.")
            else:
                with st.spinner("Creating account..."):
                    ok, msg = sign_up(email, password, name, role, region, phone)
                if ok:
                    st.success(msg)
                    st.info("Please sign in with your new account.")
                else:
                    st.error(msg)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    """Main application."""
    
    # Render hamburger and sidebar
    render_hamburger_button()
    render_custom_sidebar()
    
    # Auto-redirect after login
    if st.session_state.get("authenticated") and st.session_state.get("auth_redirect"):
        st.session_state.auth_redirect = False
        
        # Get profile
        profile = st.session_state.profile
        if profile is None and st.session_state.user:
            try:
                profile = cached_get_profile(st.session_state.user.id)
                if profile:
                    st.session_state.profile = profile
                    st.session_state.user_role = profile.get("role", "customer")
            except Exception:
                pass
        
        if profile:
            role = profile.get("role")
            pages = {
                "producer": "pages/1_producer.py",
                "merchant": "pages/2_merchant.py",
                "customer": "pages/3_customer.py",
                "admin": "pages/4_Admin.py"
            }
            if role in pages:
                try:
                    st.switch_page(pages[role])
                except Exception:
                    pass
    
    # Show content
    if st.session_state.user is None:
        show_landing()
    else:
        profile = st.session_state.profile
        if profile is None:
            try:
                profile = cached_get_profile(st.session_state.user.id)
                if profile:
                    st.session_state.profile = profile
            except Exception:
                pass
        
        if profile:
            role = profile.get("role", "customer")
            emojis = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
                        border-radius: 16px; padding: 30px 20px; text-align: center; color: white;">
                <div style="font-size: 48px;">{emojis.get(role, "👤")}</div>
                <h1 style="color: white; margin: 10px 0; font-size: 24px;">Welcome to Your Dashboard</h1>
                <p style="opacity: 0.9; font-size: 14px;">
                    👆 Tap the <strong>☰</strong> icon in the top-left corner to open the menu.
                </p>
                <p style="opacity: 0.7; font-size: 13px; margin-top: 8px;">
                    {profile.get('full_name', 'User')} · {role.capitalize()}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("📱 Tap the **☰** (hamburger) icon in the top-left corner to open the navigation menu.")
        else:
            st.warning("⚠️ Could not load profile. Please sign out and try again.")

if __name__ == "__main__":
    main()
