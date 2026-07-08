# ─────────────────────────────────────────────────────────────
# HAMBURGER MENU COMPONENT
# ─────────────────────────────────────────────────────────────

def render_hamburger_menu(profile=None):
    """
    Render a reusable hamburger menu component.
    Call this at the top of any page after st.set_page_config.
    
    Args:
        profile: User profile dict (optional, will use from session state if not provided)
    """
    
    if profile is None:
        profile = st.session_state.get("profile", {})
    
    # Get user info
    name = profile.get("full_name", "User") if profile else "Guest"
    role = profile.get("role", "customer") if profile else "guest"
    region = profile.get("region", "N/A") if profile else "N/A"
    
    # Role icon
    role_icons = {
        "producer": "🚜",
        "merchant": "🏬",
        "customer": "🛒",
        "admin": "🛡️"
    }
    role_icon = role_icons.get(role, "👤")
    
    # Check if user is logged in
    is_logged_in = st.session_state.get("user") is not None
    
    # CSS for hamburger menu
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
        transition: all 0.2s;
    }
    .hamburger-btn:hover {
        background: #2D6A4F;
        transform: scale(1.05);
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

    @media (max-width: 768px) {
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 70px !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # HTML for hamburger button and sidebar
    if is_logged_in:
        # Get verification status
        try:
            from utils.verification import check_verification_status
            verif_status = check_verification_status(st.session_state.user.id)
            if verif_status.get("is_verified", False):
                status_html = '<span class="pill pill-success">✅ Verified</span>'
            else:
                status_html = '<span class="pill pill-warning">⏳ Pending</span>'
        except Exception:
            status_html = '<span class="pill pill-neutral">⚠️ Unknown</span>'
        
        sidebar_html = f'''
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
        
        <div class="mobile-sidebar" id="mobileSidebar">
            <button class="close-sidebar-btn" onclick="
                document.getElementById('mobileSidebar').classList.remove('open');
                document.getElementById('mobileOverlay').classList.remove('active');
            ">✕</button>
            
            <div class="sidebar-profile">
                <div class="sidebar-avatar">{name[0].upper()}</div>
                <div class="sidebar-name">{name}</div>
                <div class="sidebar-role">{role_icon} {role.capitalize()} · {region}</div>
            </div>
            
            <hr class="sidebar-divider">
            
            <div class="sidebar-section-title">📊 Navigation</div>
            <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
            <button class="sidebar-nav-btn" onclick="window.location.href='pages/1_producer.py'">🚜 Producer</button>
            <button class="sidebar-nav-btn" onclick="window.location.href='pages/2_merchant.py'">🏬 Merchant</button>
            <button class="sidebar-nav-btn" onclick="window.location.href='pages/3_customer.py'">🛒 Customer</button>
            <button class="sidebar-nav-btn" onclick="window.location.href='pages/4_Admin.py'">🛡️ Admin</button>
            
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
    else:
        sidebar_html = '''
        <button class="hamburger-btn" onclick="
            var sidebar = document.getElementById('mobileSidebar');
            var overlay = document.getElementById('mobileOverlay');
            if (sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            } else {
                sidebar.classList.add('open');
                overlay.classList.add('active');
            }
        ">☰</button>
        
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
            
            <div class="sidebar-section-title">📊 Navigation</div>
            <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
            
            <hr class="sidebar-divider">
            <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🔐 Sign In</button>
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
            from utils.db_helpers import clear_data_cache
            clear_data_cache()
            st.query_params.clear()
            st.rerun()
        except Exception:
            pass


def render_hamburger_css():
    """Render only the CSS for hamburger menu (for pages that need it)."""
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarContent"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    [data-testid="stToolbar"] { display: none !important; }
    
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
    .hamburger-btn:hover { background: #2D6A4F; }
    
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
    .mobile-overlay.active { display: block; }
    
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
    .mobile-sidebar.open { transform: translateX(0); }
    
    .close-sidebar-btn {
        background: transparent;
        border: none;
        color: #e2e8f0;
        font-size: 24px;
        cursor: pointer;
        float: right;
        padding: 5px 10px;
    }
    .close-sidebar-btn:hover { color: #f87171; }
    
    .sidebar-profile { text-align: center; margin: 10px 0 20px 0; }
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
    .sidebar-name { font-size: 16px; font-weight: 600; margin-top: 8px; color: #e2e8f0; }
    .sidebar-role { font-size: 12px; color: #94a3b8; }
    .sidebar-divider { border: none; border-top: 1px solid #1e2a3a; margin: 12px 0; }
    
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
    .sidebar-nav-btn:hover { border-color: #D4A017; color: #D4A017; }
    
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
    .sidebar-nav-btn-logout:hover { background: #7f1d1d66; border-color: #ef4444; }
    
    .sidebar-section-title {
        font-weight: 600;
        color: #94a3b8;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        margin-top: 12px;
    }
    
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
    
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 70px !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
    }
    
    @media (max-width: 768px) {
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 70px !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
