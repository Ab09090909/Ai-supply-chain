"""
theme.py — Ethiopian AI Supply Chain Platform
"""
import streamlit as st

# ═══════════════════════════════════════════════════════════════
# COLOUR TOKENS
# ═══════════════════════════════════════════════════════════════
DARK = {
    "sidebar_bg":         "#161b27",
    "sidebar_border":     "#1e2a3a",
    "sidebar_text":       "#e2e8f0",
    "sidebar_subtext":    "#64748b",
    "sidebar_btn_bg":     "#1e2a3a",
    "sidebar_btn_border": "#334155",
    "sidebar_btn_color":  "#e2e8f0",
    "sidebar_divider":    "#1e2a3a",
    "pill_bg":            "#1e293b",
    "pill_color":         "#94a3b8",
    "pill_border":        "#334155",
}

LIGHT = {
    "sidebar_bg":         "#f8fafc",
    "sidebar_border":     "#e2e8f0",
    "sidebar_text":       "#1e293b",
    "sidebar_subtext":    "#64748b",
    "sidebar_btn_bg":     "#ffffff",
    "sidebar_btn_border": "#cbd5e1",
    "sidebar_btn_color":  "#1e293b",
    "sidebar_divider":    "#e2e8f0",
    "pill_bg":            "#f1f5f9",
    "pill_color":         "#475569",
    "pill_border":        "#cbd5e1",
}

def _get_tokens() -> dict:
    # Use 'theme_mode' instead of 'sidebar_light_mode' to match the toggle button
    mode = st.session_state.get("theme_mode", "dark")
    return LIGHT if mode == "light" else DARK

# ═══════════════════════════════════════════════════════════════
# INJECT GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
def inject_theme():
    """Call near the top of each page."""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
        
    t = _get_tokens()
    st.markdown(f"""
    <style>
    /* ═══════════════════════════════════════════
       RESPONSIVE UTILITIES
    ════════════════════════════════════════════ */
    @media (max-width: 768px) {{
        [data-testid="column"] {{
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}
        .dash-header h1 {{ font-size: 18px !important; }}
        .dash-header p {{ font-size: 11px !important; }}
        .dash-header {{ padding: 16px !important; gap: 12px !important; flex-wrap: wrap; }}
        .dash-header-icon {{ font-size: 28px !important; }}
        .kpi-value {{ font-size: 22px !important; }}
        .kpi-card {{ padding: 14px 16px !important; }}
        .section-title {{ font-size: 11px !important; }}
        [data-testid="stTabs"] > div > div {{ overflow-x: auto !important; -webkit-overflow-scrolling: touch; }}
        [data-testid="stTabs"] > div > div > div > button {{ font-size: 12px !important; padding: 6px 10px !important; white-space: nowrap; }}
        .record-card {{ padding: 12px !important; }}
        .price-tag {{ font-size: 15px !important; }}
        .stButton > button {{ font-size: 12px !important; padding: 8px 10px !important; }}
        .forecast-container {{ padding: 12px !important; }}
        .alert-box {{ font-size: 12px !important; }}
        .hero-section h1 {{ font-size: 24px !important; }}
        .hero-section p {{ font-size: 13px !important; }}
        .stats-grid {{ grid-template-columns: 1fr !important; }}
    }}

    @media (min-width: 769px) and (max-width: 1024px) {{
        .dash-header h1 {{ font-size: 22px !important; }}
        .kpi-value {{ font-size: 24px !important; }}
    }}

    /* ═══════════════════════════════════════════
       MAIN CONTENT — always dark
    ════════════════════════════════════════════ */
    html, body, [data-testid="stAppViewContainer"] {{
        background: #0f1117 !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* FIX: Only hide MainMenu and footer, keep header visible for sidebar toggle */
    #MainMenu, footer {{ visibility: hidden; }}
    
    /* FIX: Ensure sidebar toggle button is always visible */
    [data-testid="stSidebarCollapsedControl"] {{
        visibility: visible !important;
        display: block !important;
        position: fixed !important;
        top: 10px !important;
        right: 10px !important;
        z-index: 999999 !important;
        background: #1e2a3a !important;
        border-radius: 8px !important;
        padding: 8px !important;
    }}

    /* ═══════════════════════════════════════════
       SIDEBAR — togglable light / dark
    ════════════════════════════════════════════ */
    [data-testid="stSidebar"] {{
        background: {t["sidebar_bg"]} !important;
        border-right: 1px solid {t["sidebar_border"]} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {t["sidebar_text"]} !important;
    }}
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small {{
        color: {t["sidebar_subtext"]} !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background: {t["sidebar_btn_bg"]} !important;
        border-color: {t["sidebar_btn_border"]} !important;
        color: {t["sidebar_btn_color"]} !important;
        width: 100% !important;
        margin-bottom: 6px !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: {t["sidebar_divider"]} !important;
    }}
    [data-testid="stSidebar"] .pill {{
        background: {t["pill_bg"]} !important;
        color: {t["pill_color"]} !important;
        border-color: {t["pill_border"]} !important;
    }}
    [data-testid="stSidebar"] .pill-success {{
        background: #14532d44 !important;
        color: #16a34a !important;
        border-color: #16a34a44 !important;
    }}
    [data-testid="stSidebar"] .pill-warning {{
        background: #78350f44 !important;
        color: #d97706 !important;
        border-color: #d9770644 !important;
    }}
    [data-testid="stSidebar"] .pill-info {{
        background: #1e3a5f44 !important;
        color: #2563eb !important;
        border-color: #2563eb44 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE HEADER HELPER
# ═══════════════════════════════════════════════════════════════
def render_page_header(title: str, subtitle: str = "", icon: str = "🌾"):
    st.markdown(f"""
    <div style="
    background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
    border-radius: 14px; padding: 28px 32px; margin-bottom: 24px; color: white;
    ">
    <div style="font-size: 36px; margin-bottom: 10px;">{icon}</div>
    <h2 style="margin: 0; font-size: clamp(18px, 3vw, 26px); font-weight: 700;">{title}</h2>
    {f'<p style="margin: 6px 0 0; opacity: 0.82; font-size: 14px;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# THEME TOGGLE WIDGET
# ═══════════════════════════════════════════════════════════════
def render_theme_toggle():
    """Render a simple theme toggle button."""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
        
    if st.button("🎨 Toggle Theme", key="theme_toggle_btn", use_container_width=True):
        if st.session_state.theme_mode == "dark":
            st.session_state.theme_mode = "light"
        else:
            st.session_state.theme_mode = "dark"
        st.rerun()
