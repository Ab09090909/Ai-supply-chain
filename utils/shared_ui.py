"""
utils/shared_ui.py — Reusable hamburger menu component for all pages.

Usage (top of each page file, after st.set_page_config):
    from utils.shared_ui import render_hamburger_menu
    render_hamburger_menu()
"""
import streamlit as st


# ─────────────────────────────────────────────────────────────
# HAMBURGER MENU
# ─────────────────────────────────────────────────────────────

def render_hamburger_menu(profile=None):
    """
    Render the hamburger button + slide-out sidebar for any page.

    Call this at the top of every page (after st.set_page_config and inject_theme).
    Navigation uses st.switch_page so it works correctly on Streamlit Community Cloud.

    Args:
        profile: User profile dict. If None, reads from st.session_state.
    """
    # ── Inject sidebar CSS (shared with theme, safe to call again) ──
    from utils.theme import inject_theme
    inject_theme()

    if profile is None:
        profile = st.session_state.get("profile") or {}

    is_logged_in = st.session_state.get("user") is not None
    name    = profile.get("full_name", "User") if profile else "Guest"
    role    = profile.get("role", "customer")  if profile else "guest"
    region  = profile.get("region", "N/A")     if profile else "N/A"
    role_icon = {"producer": "🚜", "merchant": "🏬",
                 "customer": "🛒", "admin": "🛡️"}.get(role, "👤")

    # ── Session state for open/close ──
    if "menu_open" not in st.session_state:
        st.session_state.menu_open = False

    # ── Hamburger toggle button ──
    col_btn, col_spacer = st.columns([1, 11])
    with col_btn:
        label = "✕" if st.session_state.menu_open else "☰"
        if st.button(label, key="hamburger_btn_shared", help="Toggle menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    is_open = st.session_state.menu_open
    open_class    = "open"   if is_open else ""
    overlay_class = "active" if is_open else ""

    # ── Sidebar HTML (visual shell only — no JS navigation) ──
    if is_logged_in:
        try:
            from utils.verification import check_verification_status
            verif = check_verification_status(st.session_state.user.id)
            if verif.get("is_verified", False):
                status_html = '<span class="pill pill-success">✅ Verified</span>'
            elif verif.get("has_documents", False):
                status_html = '<span class="pill pill-warning">⏳ Pending</span>'
            else:
                status_html = '<span class="pill pill-info">📄 Verify</span>'
        except Exception:
            status_html = '<span class="pill pill-neutral">⚠️ Unknown</span>'

        sidebar_html = f"""
        <div class="mobile-sidebar {open_class}" id="mobileSidebar">
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
            <div class="sidebar-section-title">📌 Status</div>
            <div style="margin-bottom: 8px;">{status_html}</div>
            <hr class="sidebar-divider">
            <div class="sidebar-section-title">📊 Navigation</div>
        </div>
        <div class="mobile-overlay {overlay_class}" id="mobileOverlay" onclick="
            document.getElementById('mobileSidebar').classList.remove('open');
            this.classList.remove('active');
        "></div>
        """
    else:
        sidebar_html = f"""
        <div class="mobile-sidebar {open_class}" id="mobileSidebar">
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
        </div>
        <div class="mobile-overlay {overlay_class}" id="mobileOverlay" onclick="
            document.getElementById('mobileSidebar').classList.remove('open');
            this.classList.remove('active');
        "></div>
        """

    st.markdown(sidebar_html, unsafe_allow_html=True)

    # ── Streamlit nav buttons (only visible when menu is open) ──
    if is_open and is_logged_in:
        _render_nav_buttons(role)


def _render_nav_buttons(role: str):
    """
    Render navigation + logout buttons using st.switch_page.
    Only shown when the sidebar is open. Role-specific pages only.
    """
    from utils.auth import sign_out
    from utils.db_helpers import clear_data_cache

    role_pages = {
        "producer": ("🚜 Producer Dashboard", "pages/1_producer.py"),
        "merchant": ("🏬 Merchant Dashboard", "pages/2_merchant.py"),
        "customer": ("🛒 Customer Dashboard", "pages/3_customer.py"),
        "admin":    ("🛡️ Admin Panel",         "pages/4_Admin.py"),
    }

    # Home button
    if st.button("🏠 Home", key="nav_home_shared", use_container_width=True):
        st.switch_page("app.py")

    # Role-specific dashboard
    if role in role_pages:
        label, page = role_pages[role]
        if st.button(label, key="nav_role_shared", use_container_width=True):
            st.switch_page(page)

    st.markdown("---")

    # Logout
    if st.button("🚪 Log Out", key="nav_logout_shared", use_container_width=True):
        try:
            sign_out()
        except Exception:
            pass
        for key in ["user", "profile", "authenticated", "user_role",
                    "user_email", "auth_redirect", "menu_open"]:
            st.session_state.pop(key, None)
        try:
            clear_data_cache()
        except Exception:
            pass
        st.switch_page("app.py")


# ─────────────────────────────────────────────────────────────
# LEGACY ALIAS — kept so existing page imports don't break
# ─────────────────────────────────────────────────────────────
def render_hamburger_css():
    """
    Deprecated: CSS is now handled by inject_theme() in utils/theme.py.
    Kept as a no-op alias so existing imports don't crash.
    """
    from utils.theme import inject_theme
    inject_theme()
