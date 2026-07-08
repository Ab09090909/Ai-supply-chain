"""Producer Dashboard — MINIMAL TEST VERSION with Single Tab."""
import sys
import os
import streamlit as st

# ─────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
try:
    from utils.theme import inject_theme
    from utils.db_helpers import supabase, cached_query, clear_data_cache
    from utils.verification import check_verification_status
except ImportError as e:
    st.error(f"⚠️ Import error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Producer Dashboard",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# ─────────────────────────────────────────────
# THEME INJECTION
# ─────────────────────────────────────────────
inject_theme()

# ─────────────────────────────────────────────────────────────
# CSS - HIDE SIDEBAR, CUSTOM HAMBURGER MENU
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

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 70px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HAMBURGER MENU
# ─────────────────────────────────────────────────────────────
def render_hamburger_menu():
    """Render the hamburger menu."""
    
    # Get profile
    profile = st.session_state.get("profile", {})
    name = profile.get("full_name", "User") if profile else "User"
    
    # HTML for hamburger
    st.markdown(f'''
    <button class="hamburger-btn" onclick="
        var sidebar = document.getElementById('mobileSidebar');
        var overlay = document.getElementById('mobileOverlay');
        if (sidebar.classList.contains('open')) {{
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        }} else {{
            sidebar.classList.add('open');
            overlay.classList.add('active');
        }}
    ">☰</button>
    ''', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CUSTOM SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_custom_sidebar(profile, user_id, role):
    """Render custom sidebar."""
    
    if not profile:
        st.markdown('''
        <div class="mobile-sidebar" id="mobileSidebar">
            <button class="close-sidebar-btn" onclick="
                document.getElementById('mobileSidebar').classList.remove('open');
                document.getElementById('mobileOverlay').classList.remove('active');
            ">✕</button>
            <div class="sidebar-profile">
                <div class="sidebar-avatar">🔐</div>
                <div class="sidebar-name">Not Signed In</div>
                <div class="sidebar-role">Please sign in</div>
            </div>
            <hr class="sidebar-divider">
            <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
        </div>
        <div class="mobile-overlay" id="mobileOverlay" onclick="
            document.getElementById('mobileSidebar').classList.remove('open');
            this.classList.remove('active');
        "></div>
        ''', unsafe_allow_html=True)
        return
    
    name = profile.get("full_name", "User")
    region = profile.get("region", "N/A")
    
    # Verification status
    try:
        verif_status = check_verification_status(user_id)
        if verif_status.get("is_verified", False):
            status_html = '<span class="pill pill-success">✅ Verified</span>'
        else:
            status_html = '<span class="pill pill-warning">⏳ Pending</span>'
    except Exception:
        status_html = '<span class="pill pill-neutral">⚠️ Unknown</span>'
    
    sidebar_html = f'''
    <div class="mobile-sidebar" id="mobileSidebar">
        <button class="close-sidebar-btn" onclick="
            document.getElementById('mobileSidebar').classList.remove('open');
            document.getElementById('mobileOverlay').classList.remove('active');
        ">✕</button>
        
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{name[0].upper()}</div>
            <div class="sidebar-name">{name}</div>
            <div class="sidebar-role">🚜 Producer · {region}</div>
        </div>
        
        <hr class="sidebar-divider">
        
        <div class="sidebar-section-title">📊 Navigation</div>
        <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
        <button class="sidebar-nav-btn" onclick="window.location.href='pages/1_producer.py'">🚜 Producer</button>
        
        <hr class="sidebar-divider">
        
        <div class="sidebar-section-title">📌 Status</div>
        <div style="margin-bottom: 8px;">{status_html}</div>
        
        <hr class="sidebar-divider">
        <button class="sidebar-nav-btn-logout" onclick="window.location.href = window.location.pathname + '?logout=true';">🚪 Log Out</button>
    </div>
    <div class="mobile-overlay" id="mobileOverlay" onclick="
        document.getElementById('mobileSidebar').classList.remove('open');
        this.classList.remove('active');
    "></div>
    '''
    
    st.markdown(sidebar_html, unsafe_allow_html=True)
    
    # Handle logout
    if st.query_params.get("logout") == "true":
        try:
            from utils.auth import sign_out
            sign_out()
            st.session_state.user = None
            st.session_state.profile = None
            st.session_state.authenticated = False
            clear_data_cache()
            st.query_params.clear()
            st.rerun()
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────
# AUTH GUARD
# ─────────────────────────────────────────────────────────────
def check_auth():
    if st.session_state.get("user") is None:
        st.warning("⚠️ Please sign in first.")
        st.page_link("app.py", label="← Go to Login", icon="🔐")
        st.stop()
        return False
    
    profile = st.session_state.get("profile")
    if profile is None or profile.get("role") != "producer":
        st.error("🚫 Access denied. This page is for producers only.")
        st.page_link("app.py", label="← Go to Login", icon="🔐")
        st.stop()
        return False
    
    return True

if not check_auth():
    st.stop()

# ─────────────────────────────────────────────────────────────
# GET USER DATA
# ─────────────────────────────────────────────────────────────
profile = st.session_state.get("profile", {})
user_id = st.session_state.user.id
verif_status = check_verification_status(user_id)

# ─────────────────────────────────────────────────────────────
# RENDER HAMBURGER MENU AND SIDEBAR
# ─────────────────────────────────────────────────────────────
render_hamburger_menu()
render_custom_sidebar(profile, user_id, "producer")

# ─────────────────────────────────────────────────────────────
# SINGLE TAB - OVERVIEW
# ─────────────────────────────────────────────────────────────
st.title("🚜 Producer Dashboard")

# Simple header
st.markdown(f"""
<div style="background: #161b27; border: 1px solid #1e2a3a; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;">
    <p style="margin: 0; font-size: 14px; color: #e2e8f0;">
        👤 {profile.get('full_name', 'Producer')} · 📍 {profile.get('region', 'N/A')}
        <span style="float: right; color: #4ade80;">{'✅ Verified' if verif_status.get('is_verified', False) else '⏳ Pending'}</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Simple overview
try:
    my_products = cached_query("products", filters={"producer_id": user_id}, limit=500)
    total_products = len(my_products)
    active_products = sum(1 for p in my_products if p.get("is_available", False))
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", total_products)
    c2.metric("Active Products", active_products)
    c3.metric("Inactive", total_products - active_products)
    
    if my_products:
        st.markdown("---")
        st.markdown("### 📦 Your Products")
        for p in my_products[:5]:
            with st.container(border=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{p.get('product_name', 'Unknown')}**")
                    st.caption(f"{p.get('sector', '—')} · {p.get('region', '—')}")
                with col2:
                    st.caption(f"Stock: {p.get('quantity', 0)} {p.get('unit', '')}")
                    st.caption(f"Price: {p.get('price_birr', 0):,.0f} Birr")
    else:
        st.info("No products listed yet. Add your first product!")
        
except Exception as e:
    st.error(f"⚠️ Error: {str(e)}")

st.markdown("---")
st.caption("✅ If you can see this page and the hamburger menu works, the test is successful!")
