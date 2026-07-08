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
    initial_sidebar_state="expanded",  # Keep sidebar expanded by default
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

# Inject theme
inject_theme()

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS FOR MOBILE SIDEBAR
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── FIX MOBILE SIDEBAR ─── */
/* Make sure sidebar is always accessible on mobile */
@media (max-width: 768px) {
    /* Ensure sidebar hamburger menu is visible */
    [data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 300px !important;
        width: 280px !important;
    }
    
    /* Make sure the sidebar toggle button is visible */
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        background: #1B4332 !important;
        color: white !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        border: none !important;
        cursor: pointer !important;
        font-size: 18px !important;
    }
    
    /* Sidebar overlay for mobile */
    [data-testid="stSidebarOverlay"] {
        display: block !important;
    }
    
    /* Make sidebar content scrollable on mobile */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        overflow-y: auto !important;
        max-height: 100vh !important;
    }
    
    /* Adjust main content padding for mobile */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 60px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
    
    /* Fix hamburger menu button */
    button[kind="header"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        background: #1B4332 !important;
        color: white !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        border: none !important;
        font-size: 20px !important;
    }
}

/* ─── SIDEBAR STYLES ─── */
[data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #1e2a3a !important;
    padding-top: 20px !important;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: #64748b !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    width: 100% !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    padding: 10px 14px !important;
    margin-bottom: 4px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #D4A017 !important;
    color: #D4A017 !important;
}

[data-testid="stSidebar"] hr {
    border-color: #1e2a3a !important;
    margin: 12px 0 !important;
}

[data-testid="stSidebar"] .stInfo {
    background: #1e2a3a !important;
    border-color: #334155 !important;
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

/* ─── HIDE STREAMLIT BRANDING ─── */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

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
    [data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 280px !important;
    }
    .kpi-value { font-size: 22px !important; }
    .kpi-card { padding: 14px 16px !important; }
    div.stButton > button { width: 100% !important; }
    [data-testid="stTabs"] > div > div > div > button {
        font-size: 12px !important;
        padding: 6px 10px !important;
    }
    [data-testid="column"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 60px !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
    
    /* Make hamburger menu clearly visible */
    button[data-testid="baseButton-header"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        background: #1B4332 !important;
        color: white !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        border: 1px solid #2D6A4F !important;
        font-size: 20px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
    }
    
    /* Sidebar overlay fix */
    [data-testid="stSidebarOverlay"] {
        display: block !important;
        background: rgba(0,0,0,0.5) !important;
        z-index: 99999 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
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
    else:
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
                "producer": "pages/1_producer.py",
                "merchant": "pages/2_merchant.py",
                "customer": "pages/3_customer.py",
                "admin": "pages/4_Admin.py"
            }
            
            if role in nav_pages:
                icons = {
                    "producer": "🚜 Producer",
                    "merchant": "🏬 Merchant",
                    "customer": "🛒 Customer",
                    "admin": "🛡️ Admin"
                }
                if st.button(icons.get(role, "Dashboard"), key=f"nav_{role}", use_container_width=True):
                    try:
                        st.switch_page(nav_pages[role])
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
                border-radius: 16px; padding: 40px; text-align: center; color: white; margin-bottom: 30px;">
        <h1 style="font-size: 36px; margin: 0; color: white;">🌾 Ethiopian AI Supply Chain</h1>
        <p style="font-size: 16px; opacity: 0.9; margin-top: 10px;">
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
                        border-radius: 16px; padding: 40px; text-align: center; color: white;">
                <div style="font-size: 48px;">{emojis.get(role, "👤")}</div>
                <h1 style="color: white; margin: 10px 0;">Welcome to Your Dashboard</h1>
                <p style="opacity: 0.9; font-size: 16px;">
                    👆 Tap the <strong>☰</strong> icon in the top-left corner to open the sidebar.
                </p>
                <p style="opacity: 0.7; font-size: 14px; margin-top: 8px;">
                    {profile.get('full_name', 'User')} · {role.capitalize()}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mobile instructions
            st.info("📱 On mobile: Tap the **☰** (hamburger) icon in the top-left corner to open the sidebar menu.")
        else:
            st.warning("⚠️ Could not load profile. Please sign out and try again.")

if __name__ == "__main__":
    main()
