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
    initial_sidebar_state="expanded",
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
if "mobile_menu_open" not in st.session_state:
    st.session_state.mobile_menu_open = False

# Inject theme
inject_theme()

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS FOR MOBILE SIDEBAR
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── MOBILE FIRST ─── */
* {
    box-sizing: border-box;
}

/* ─── CUSTOM MOBILE SIDEBAR ─── */
.mobile-sidebar {
    display: none;
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
    transition: transform 0.3s ease;
}

.mobile-sidebar.open {
    display: block;
    transform: translateX(0);
}

.mobile-sidebar.closed {
    display: block;
    transform: translateX(-100%);
}

.mobile-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.6);
    z-index: 999998;
}

.mobile-overlay.active {
    display: block;
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
    display: none;
}

.hamburger-btn:hover {
    background: #2D6A4F;
}

/* ─── CLOSE BUTTON ON SIDEBAR ─── */
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

/* ─── SIDEBAR CONTENT STYLES ─── */
.sidebar-profile {
    text-align: center;
    margin: 10px 0;
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
    border-color: #1e2a3a;
    margin: 12px 0;
}

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

/* ─── DESKTOP SIDEBAR ─── */
@media (min-width: 769px) {
    [data-testid="stSidebar"] {
        display: block !important;
        width: 300px !important;
        min-width: 300px !important;
        background: #161b27 !important;
        border-right: 1px solid #1e2a3a !important;
    }
    
    .hamburger-btn {
        display: none !important;
    }
    
    .mobile-sidebar {
        display: none !important;
    }
    
    .mobile-overlay {
        display: none !important;
    }
}

/* ─── MOBILE SIDEBAR ─── */
@media (max-width: 768px) {
    /* Hide Streamlit default sidebar on mobile */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Show hamburger button */
    .hamburger-btn {
        display: block !important;
    }
    
    /* Show custom sidebar when open */
    .mobile-sidebar.open {
        display: block !important;
        transform: translateX(0) !important;
    }
    
    .mobile-sidebar.closed {
        transform: translateX(-100%) !important;
    }
    
    .mobile-overlay.active {
        display: block !important;
    }
    
    /* Main content padding */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 70px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }
    
    /* Fix tabs scrolling */
    [data-testid="stTabs"] > div > div {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }
    
    [data-testid="stTabs"] > div > div > div > button {
        font-size: 12px !important;
        padding: 6px 10px !important;
        white-space: nowrap !important;
    }
}

/* ─── STREAMLIT OVERRIDES ─── */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

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
.pill-purple { background: #3b1a6044; color: #a78bfa; border: 1px solid #7c3aed44; }
.pill-neutral { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

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

/* ─── KPI CARDS ─── */
.kpi-card {
    background: #161b27 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 10px;
    padding: 16px 20px;
    height: 100%;
}
.kpi-label { font-size: 11px; font-weight: 600; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
.kpi-value { font-size: 24px; font-weight: 700; color: #f1f5f9 !important; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.kpi-sub { font-size: 12px; color: #64748b !important; margin-top: 6px; }

/* ─── ALERT BOXES ─── */
.alert-box { border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; border: 1px solid; }
.alert-warning { background: #78350f22; border-color: #d9770666; color: #fbbf24; }
.alert-danger { background: #7f1d1d22; border-color: #ef444466; color: #f87171; }
.alert-info { background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }
.alert-success { background: #14532d22; border-color: #16a34a66; color: #4ade80; }
.alert-purple { background: #3b1a6022; border-color: #7c3aed66; color: #a78bfa; }

/* ─── SECTION TITLE ─── */
.section-title {
    font-size: 13px;
    font-weight: 700;
    color: #475569 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 20px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2a3a;
}

/* ─── CONFIRM BOX ─── */
.confirm-box { background: #7f1d1d22; border: 1px solid #ef444455; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #fca5a5; margin-bottom: 8px; }

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    .kpi-value { font-size: 20px !important; }
    .kpi-card { padding: 12px 14px !important; }
    div.stButton > button { width: 100% !important; }
    [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CUSTOM MOBILE SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_mobile_sidebar():
    """Render custom mobile sidebar."""
    
    # Get profile
    profile = st.session_state.profile
    if profile is None and st.session_state.user:
        try:
            profile = cached_get_profile(st.session_state.user.id)
            if profile:
                st.session_state.profile = profile
        except Exception:
            pass
    
    if profile:
        name = profile.get("full_name", "User")
        role = profile.get("role", "customer")
        region = profile.get("region", "N/A")
        
        # Sidebar HTML
        sidebar_html = f'''
        <div class="mobile-sidebar { 'open' if st.session_state.mobile_menu_open else 'closed' }" id="mobileSidebar">
            <button class="close-sidebar-btn" onclick="document.getElementById('mobileSidebar').classList.remove('open'); document.getElementById('mobileSidebar').classList.add('closed'); document.getElementById('mobileOverlay').classList.remove('active');">✕</button>
            
            <div class="sidebar-profile">
                <div class="sidebar-avatar">{name[0].upper()}</div>
                <div class="sidebar-name">{name}</div>
                <div class="sidebar-role">{role.capitalize()} · {region}</div>
            </div>
            
            <hr class="sidebar-divider">
            
            <div style="font-weight: 600; color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">📊 Navigation</div>
            
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
            status = check_verification_status(st.session_state.user.id)
            if status.get("is_verified", False):
                status_html = '<span class="pill pill-success">✅ Verified</span>'
            elif status.get("has_documents", False):
                status_html = '<span class="pill pill-warning">⏳ Pending</span>'
            else:
                status_html = '<span class="pill pill-info">📄 Verify</span>'
        except Exception:
            status_html = '<span class="pill pill-neutral">⚠️ Unknown</span>'
        
        sidebar_html += f'''
            <hr class="sidebar-divider">
            <div style="font-weight: 600; color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">📌 Status</div>
            <div style="margin-bottom: 8px;">{status_html}</div>
            <hr class="sidebar-divider">
            <button class="sidebar-nav-btn" style="color: #f87171;" onclick="document.getElementById('logoutForm').submit();">🚪 Log Out</button>
        </div>
        '''
        
        st.markdown(sidebar_html, unsafe_allow_html=True)
        
        # Logout form
        st.markdown('''
        <form id="logoutForm" method="post" action="">
            <input type="hidden" name="logout" value="true">
        </form>
        ''', unsafe_allow_html=True)
        
        # Handle logout from form
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
# HAMBURGER MENU BUTTON
# ─────────────────────────────────────────────────────────────
def render_hamburger_button():
    """Render the hamburger menu button."""
    st.markdown('''
    <button class="hamburger-btn" onclick="
        var sidebar = document.getElementById('mobileSidebar');
        var overlay = document.getElementById('mobileOverlay');
        if (sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            sidebar.classList.add('closed');
            overlay.classList.remove('active');
        } else {
            sidebar.classList.remove('closed');
            sidebar.classList.add('open');
            overlay.classList.add('active');
        }
    ">☰</button>
    <div class="mobile-overlay" id="mobileOverlay" onclick="
        document.getElementById('mobileSidebar').classList.remove('open');
        document.getElementById('mobileSidebar').classList.add('closed');
        this.classList.remove('active');
    "></div>
    ''', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DESKTOP SIDEBAR (Streamlit native)
# ─────────────────────────────────────────────────────────────
def render_desktop_sidebar():
    """Render desktop sidebar using Streamlit native."""
    with st.sidebar:
        # Theme toggle
        render_theme_toggle()
        st.markdown("---")
        
        st.markdown("## 🌾 AI Supply Chain")
        st.markdown("Ethiopian Multi-Sector Commerce")
        st.markdown("---")
        
        # ─── USER STATUS ───
        if st.session_state.user is None:
            st.info("🔐 Please sign in")
            return
        
        # Get profile
        profile = st.session_state.profile
        if profile is None:
            try:
                profile = cached_get_profile(st.session_state.user.id)
                if profile:
                    st.session_state.profile = profile
            except Exception:
                pass
        
        if profile:
            # Show user info
            name = profile.get("full_name", "User")
            role = profile.get("role", "customer")
            region = profile.get("region", "N/A")
            
            st.markdown(f"""
            <div style="text-align: center; margin: 10px 0;">
                <div style="width: 60px; height: 60px; border-radius: 50%; background: #1e2a3a; 
                     display: flex; align-items: center; justify-content: center; margin: 0 auto; 
                     font-size: 24px; color: #f1f5f9; font-weight: 700; border: 2px solid #D4A017;">
                    {name[0].upper()}
                </div>
                <div style="font-size: 16px; font-weight: 600; margin-top: 8px; color: #e2e8f0;">{name}</div>
                <div style="font-size: 12px; color: #94a3b8;">{role.capitalize()} · {region}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ─── NAVIGATION ───
            st.markdown("### 📊 Navigation")
            
            # Home
            if st.button("🏠 Home", key="nav_home", use_container_width=True):
                st.switch_page("app.py")
            
            # Role-specific pages
            nav_pages = {
                "producer": ("🚜 Producer", "pages/1_producer.py"),
                "merchant": ("🏬 Merchant", "pages/2_merchant.py"),
                "customer": ("🛒 Customer", "pages/3_customer.py"),
                "admin": ("🛡️ Admin", "pages/4_Admin.py")
            }
            
            if role in nav_pages:
                label, page = nav_pages[role]
                if st.button(label, key=f"nav_{role}", use_container_width=True):
                    try:
                        st.switch_page(page)
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            st.markdown("---")
            
            # ─── VERIFICATION STATUS ───
            try:
                status = check_verification_status(st.session_state.user.id)
                if status.get("is_verified", False):
                    st.markdown('<span class="pill pill-success">✅ Verified</span>', unsafe_allow_html=True)
                elif status.get("has_documents", False):
                    st.markdown('<span class="pill pill-warning">⏳ Pending</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="pill pill-info">📄 Verify</span>', unsafe_allow_html=True)
            except Exception:
                pass
            
            st.markdown("---")
            
            # ─── LOGOUT ───
            if st.button("🚪 Log Out", key="logout_btn", use_container_width=True):
                try:
                    sign_out()
                    st.session_state.user = None
                    st.session_state.profile = None
                    st.session_state.authenticated = False
                    st.session_state.user_role = None
                    clear_data_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Logout error: {e}")

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
        role = st.selectbox("I am a...", ["producer", "merchant", "customer"])
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
    
    # Check if user is logged in
    is_logged_in = st.session_state.user is not None
    
    # Render appropriate sidebar
    if is_logged_in:
        # Show hamburger on mobile, desktop sidebar on desktop
        render_hamburger_button()
        render_mobile_sidebar()
        render_desktop_sidebar()  # This renders inside st.sidebar
    
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
    if not is_logged_in:
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
            
            # Mobile instructions
            st.info("📱 On mobile: Tap the **☰** (hamburger) icon in the top-left corner.")
        else:
            st.warning("⚠️ Could not load profile. Please sign out and try again.")

if __name__ == "__main__":
    main()
