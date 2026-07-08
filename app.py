"""
app.py — Ethiopian AI Supply Chain Platform (Main Entry)
"""
import sys
import os
import streamlit as st
import logging
from dotenv import load_dotenv

# Load environment variables from .env (local development only)
load_dotenv()

# ─────────────────────────────────────────────────────────────
# STREAMLIT CLOUD SECRETS BRIDGE (SECURE)
# ─────────────────────────────────────────────────────────────
REQUIRED_SECRETS = [
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'SUPABASE_SERVICE_ROLE',
    'GROQ_API_KEY',
    'APP_SECRET_KEY',
    'ADMIN_PASSWORD'
]

if hasattr(st, 'secrets') and st.secrets:
    for key in REQUIRED_SECRETS:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────
try:
    from utils.theme import inject_theme, render_theme_toggle
    from utils.auth import sign_in, sign_up, sign_out, forgot_password
    from utils.constants import REGIONS, SECTORS, SESSION_KEYS
    from utils.db_helpers import supabase, cached_get_profile, cached_unread_count, clear_data_cache
    from utils.verification import check_verification_status
    from utils.shared_ui import render_profile_editor_modal
except ImportError as e:
    st.error(f"⚠️ Import error: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'user': None,
        'profile': None,
        'authenticated': False,
        'user_role': None,
        'user_email': None,
        'theme_mode': 'dark',
        'show_profile_editor': False,
        'sidebar_light_mode': False,
        'auth_redirect': False,
        'nav_clicked': False,
        'page': 'main'
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize SESSION_KEYS from constants
    if 'SESSION_KEYS' in globals():
        for _k in SESSION_KEYS:
            if _k not in st.session_state:
                st.session_state[_k] = None

initialize_session_state()

# Inject theme
inject_theme()

# ═════════════════════════════════════════════════════════════
# SIDEBAR RENDERER (COMPLETELY REWRITTEN)
# ═════════════════════════════════════════════════════════════
def render_sidebar():
    """Render the sidebar with navigation and user info."""
    
    # Always render sidebar container
    with st.sidebar:
        # ─── THEME TOGGLE ───
        render_theme_toggle()
        st.divider()
        
        # ─── CHECK IF USER IS LOGGED IN ───
        if st.session_state.get("user") is None:
            st.info("👈 Please sign in using the main page")
            return None, None
        
        # ─── USER IS LOGGED IN ───
        st.markdown("## 🌾 AI Supply Chain")
        st.caption("Ethiopian Multi-Sector Commerce")
        st.divider()
        
        # ─── GET PROFILE ───
        profile = st.session_state.get("profile")
        if profile is None and st.session_state.get("user"):
            try:
                profile = cached_get_profile(st.session_state.user.id)
                if profile:
                    st.session_state.profile = profile
            except Exception as e:
                logger.error(f"Profile fetch error: {e}")
        
        if profile is None:
            st.warning("⚠️ Could not load profile")
            if st.button("🚪 Sign Out", key="sb_logout_error", use_container_width=True):
                sign_out()
                st.rerun()
            return None, None
        
        role = profile.get("role", "customer")
        st.session_state.user_role = role
        
        # ─── PROFILE PICTURE ───
        profile_pic = profile.get("profile_image")
        if profile_pic:
            st.markdown(f"""
            <div style="text-align: center; margin: 15px 0;">
                <img src="data:image/jpeg;base64,{profile_pic}" 
                     style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid #D4A017; object-fit: cover;">
            </div>
            """, unsafe_allow_html=True)
        else:
            name_initial = profile.get("full_name", "U")[0].upper()
            st.markdown(f"""
            <div style="text-align: center; margin: 15px 0;">
                <div style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid #D4A017; background: #1e2a3a; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 32px; color: #f1f5f9; font-weight: 700;">
                    {name_initial}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ─── USER NAME ───
        st.markdown(f"""
        <div style="text-align: center; margin: 10px 0;">
            <div style="font-size: 18px; font-weight: 700; color: #f1f5f9;">{profile.get('full_name', 'User')}</div>
            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">{role.capitalize()}</div>
            <div style="font-size: 11px; color: #64748b;">📍 {profile.get('region', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ─── EDIT PROFILE BUTTON ───
        if st.button("✏️ Edit Profile", key="edit_profile_sidebar", use_container_width=True):
            st.session_state.show_profile_editor = True
            st.rerun()
        
        st.divider()
        
        # ─── NAVIGATION ───
        st.markdown("### 📊 Navigation")
        
        # Role-specific dashboard
        nav_pages = {
            "producer": ("🚜 Producer Dashboard", "pages/1_producer.py"),
            "merchant": ("🏬 Merchant Dashboard", "pages/2_merchant.py"),
            "customer": ("🛒 Customer Dashboard", "pages/3_customer.py"),
            "admin": ("🛡️ Admin Panel", "pages/4_Admin.py")
        }
        
        if role in nav_pages:
            label, page = nav_pages[role]
            if st.button(label, key=f"nav_{role}", use_container_width=True):
                try:
                    st.switch_page(page)
                except Exception as e:
                    st.error(f"Navigation error: {e}")
        
        # Home
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            try:
                st.switch_page("app.py")
            except Exception:
                pass
        
        st.divider()
        
        # ─── STATUS ───
        st.markdown("### 📌 Status")
        
        # Verification
        try:
            verif_status = check_verification_status(st.session_state.user.id)
            if verif_status.get("is_verified", False):
                st.markdown('<span class="pill pill-success">✅ Verified</span>', unsafe_allow_html=True)
            elif verif_status.get("has_documents", False):
                st.markdown('<span class="pill pill-warning">⏳ Pending</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pill pill-info">📄 Verify</span>', unsafe_allow_html=True)
        except Exception:
            pass
        
        # Notifications
        try:
            unread = cached_unread_count(st.session_state.user.id)
            if unread and unread > 0:
                st.info(f"🔔 {unread} unread")
        except Exception:
            pass
        
        st.divider()
        
        # ─── LOGOUT ───
        if st.button("🚪 Log Out", key="sb_logout_btn", use_container_width=True):
            try:
                sign_out()
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.profile = None
                st.session_state.user_role = None
                clear_data_cache()
                st.rerun()
            except Exception as e:
                st.error(f"Logout error: {e}")
        
        # Footer
        st.divider()
        st.caption("🌾 v2.0")
        
        return profile, role

# ═════════════════════════════════════════════════════════════
# LANDING PAGE
# ═════════════════════════════════════════════════════════════
def show_landing():
    """Show the landing page with login/register."""
    
    # Stats
    try:
        _n_products = supabase.table("products").select("", count="exact").eq("is_available", True).execute().count or 0
    except Exception:
        _n_products = 0
    
    try:
        _n_users = supabase.table("profiles").select("", count="exact").execute().count or 0
    except Exception:
        _n_users = 0
    
    _n_sectors = len(SECTORS) if 'SECTORS' in globals() else 0
    
    # Hero Section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 55%, #40916C 100%); border-radius: 20px; padding: 40px 36px; margin-bottom: 30px; color: white;">
        <p style="font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#F4C430;">🌍 Wolaita Sodo University · ECE</p>
        <h1 style="font-size: clamp(24px, 4vw, 40px); font-weight: 800; margin: 10px 0; color: white;">Ethiopian <span style="color: #F4C430;">AI Supply Chain</span></h1>
        <p style="font-size: 14px; color: rgba(255,255,255,0.82); line-height: 1.7; max-width: 560px;">AI-powered matching, real-time price intelligence, and fraud-resistant trade agreements.</p>
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px;">
            <span style="background: #D4A017; color: #1B4332; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 700;">🤖 AI Price Engine</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 4px 14px; border-radius: 20px; font-size: 12px;">🤝 Smart Matchmaking</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 4px 14px; border-radius: 20px; font-size: 12px;">🛡️ Fraud Detection</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 4px 14px; border-radius: 20px; font-size: 12px;">📈 Demand Forecasting</span>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 24px;">
        <div style="background: #161b27; border: 1px solid #1e2a3a; border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: #4ade80;">{_n_products}</div>
            <div style="font-size: 11px; color: #64748b;">Listings</div>
        </div>
        <div style="background: #161b27; border: 1px solid #1e2a3a; border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: #60a5fa;">{_n_users}</div>
            <div style="font-size: 11px; color: #64748b;">Users</div>
        </div>
        <div style="background: #161b27; border: 1px solid #1e2a3a; border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: #a78bfa;">{_n_sectors}</div>
            <div style="font-size: 11px; color: #64748b;">Sectors</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register
    st.markdown('<div style="background: #161b27; border: 1px solid #1e2a3a; border-radius: 16px; padding: 28px 24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 18px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px;">🔐 Access Your Account</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: #64748b; margin-bottom: 20px;">Sign in or register below.</div>', unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register"])
    
    with tab_login:
        email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
        
        if st.button("Sign In →", use_container_width=True, type="primary", key="login_btn"):
            if not email or not password:
                st.warning("Please enter your email and password.")
            else:
                with st.spinner("Authenticating…"):
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
    
    with tab_register:
        reg_name = st.text_input("Full Name", key="reg_name", placeholder="Abebe Girma")
        reg_email = st.text_input("Email", key="reg_email", placeholder="abebe@example.com")
        reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min. 8 characters")
        
        col_r, col_reg = st.columns(2)
        with col_r:
            reg_role = st.selectbox("I am a…", ["producer", "merchant", "customer"], key="reg_role")
        with col_reg:
            reg_region = st.selectbox("Region", REGIONS if 'REGIONS' in globals() else ["Addis Ababa"], key="reg_region")
        
        reg_phone = st.text_input("Phone (optional)", key="reg_phone", placeholder="+251 9xx xxx xxx")
        
        if st.button("Create Account →", use_container_width=True, type="primary", key="reg_btn"):
            if not all([reg_name, reg_email, reg_password]):
                st.warning("Name, email, and password are required.")
            else:
                with st.spinner("Creating account…"):
                    ok, msg = sign_up(reg_email, reg_password, reg_name, reg_role, reg_region, reg_phone)
                if ok:
                    st.success(msg)
                    st.info("Account created — please sign in.")
                else:
                    st.error(msg)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═════════════════════════════════════════════════════════════
def main():
    """Main application entry point."""
    
    # Render sidebar
    profile, role = render_sidebar()
    
    # ─── PROFILE EDITOR MODAL ───
    if st.session_state.get("show_profile_editor") and profile:
        st.markdown("""
        <style>
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        @media (max-width: 768px) {
            .modal-overlay {
                padding: 10px;
                align-items: flex-start;
                padding-top: 40px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            render_profile_editor_modal(profile, st.session_state.user.id)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    # ─── AUTO-REDIRECT ───
    if st.session_state.get("authenticated") and st.session_state.get("auth_redirect"):
        st.session_state.auth_redirect = False
        
        if profile is None and st.session_state.get("user"):
            try:
                profile = cached_get_profile(st.session_state.user.id)
                if profile:
                    st.session_state.profile = profile
                    st.session_state.user_role = profile.get("role", "customer")
            except Exception:
                pass
        
        if profile:
            role = profile.get("role")
            page_mapping = {
                "producer": "pages/1_producer.py",
                "merchant": "pages/2_merchant.py",
                "customer": "pages/3_customer.py",
                "admin": "pages/4_Admin.py"
            }
            if role in page_mapping:
                try:
                    st.switch_page(page_mapping[role])
                except Exception:
                    pass
    
    # ─── SHOW LANDING OR DASHBOARD ───
    if st.session_state.get("user") is None or not st.session_state.get("authenticated"):
        show_landing()
    else:
        if profile is None:
            st.error("⚠️ Could not load profile. Please sign out and try again.")
            if st.button("Sign Out", key="main_signout_error", use_container_width=True):
                try:
                    sign_out()
                    st.session_state.authenticated = False
                    st.session_state.user = None
                    st.session_state.profile = None
                    clear_data_cache()
                    st.rerun()
                except Exception:
                    pass
        else:
            role = profile.get("role", "customer")
            role_emoji = {
                "producer": "🚜", 
                "merchant": "🏬", 
                "customer": "🛒", 
                "admin": "🛡️"
            }.get(role, "👤")
            
            # Dashboard Home
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
                        border-radius: 14px; padding: 36px; color: white; text-align: center;">
                <div style="font-size: 56px; margin-bottom: 12px;">{role_emoji}</div>
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Your Dashboard</h1>
                <p style="opacity: 0.9; margin-top: 10px; font-size: 15px;">
                    👈 Use the sidebar navigation to go to your dashboard.
                </p>
                <p style="opacity: 0.7; margin-top: 6px; font-size: 13px;">
                    {profile.get('full_name', 'User')} · <strong>{role.capitalize()}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick stats
            try:
                if role == "producer":
                    prod_count = supabase.table("products").select("id", count="exact").eq("producer_id", st.session_state.user.id).execute().count or 0
                    st.markdown(f"""
                    <div style="background: #161b27; border: 1px solid #1e2a3a; border-radius: 10px; padding: 16px; margin-top: 16px;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; text-align: center;">
                            <div>
                                <div style="font-size: 24px; font-weight: 700; color: #4ade80;">{prod_count}</div>
                                <div style="font-size: 11px; color: #64748b;">Products</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                pass

# ─────────────────────────────────────────────────────────────
# RUN APP
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
