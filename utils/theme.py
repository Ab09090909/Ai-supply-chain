"""
theme.py — Minimal theme for sidebar with mobile support
"""
import streamlit as st

def inject_theme():
    """Inject minimal theme CSS."""
    # Define accent colors
    is_light = st.session_state.get("sidebar_light_mode", False)
    accent = "#D4A017" if not is_light else "#1B4332"
    accent_light = "#F4C430" if not is_light else "#2D6A4F"
    
    st.markdown(f"""
<style>
/* ─── BASE ─── */
html, body, [data-testid="stAppViewContainer"] {{
    background: #0f1117 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif;
}}

/* ─── MOBILE SIDEBAR FIX ─── */
@media (max-width: 768px) {{
    /* Make hamburger menu visible */
    button[data-testid="baseButton-header"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        background: #1B4332 !important;
        color: white !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        border: 2px solid #2D6A4F !important;
        font-size: 22px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
    }}
    
    /* Ensure sidebar is accessible */
    [data-testid="stSidebar"] {{
        width: 280px !important;
        min-width: 280px !important;
        max-width: 300px !important;
        z-index: 999998 !important;
    }}
    
    /* Sidebar overlay */
    [data-testid="stSidebarOverlay"] {{
        display: block !important;
        z-index: 999997 !important;
        background: rgba(0,0,0,0.5) !important;
    }}
    
    /* Main content padding for mobile */
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 70px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }}
}}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {{
    background: #161b27 !important;
    border-right: 1px solid #1e2a3a !important;
    padding-top: 20px !important;
}}

[data-testid="stSidebar"] * {{
    color: #e2e8f0 !important;
}}

[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {{
    color: #64748b !important;
}}

[data-testid="stSidebar"] .stButton > button {{
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    width: 100% !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    padding: 10px 14px !important;
    margin-bottom: 4px !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {accent}55 !important;
    color: {accent} !important;
}}

[data-testid="stSidebar"] hr {{
    border-color: #1e2a3a !important;
    margin: 12px 0 !important;
}}

[data-testid="stSidebar"] .stInfo {{
    background: #1e2a3a !important;
    border-color: #334155 !important;
}}

/* ─── PILL STYLES ─── */
.pill {{
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.3px;
    margin: 2px 0;
}}
.pill-success {{ background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }}
.pill-warning {{ background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }}
.pill-danger {{ background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }}
.pill-info {{ background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }}
.pill-purple {{ background: #3b1a6044; color: #a78bfa; border: 1px solid #7c3aed44; }}
.pill-neutral {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; }}

/* ─── HIDE STREAMLIT BRANDING ─── */
#MainMenu, footer, header {{ visibility: hidden !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}

/* ─── BUTTONS ─── */
.stButton > button {{
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    background: #1e2a3a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    cursor: pointer !important;
}}

.stButton > button:hover {{
    border-color: {accent}55 !important;
    color: {accent} !important;
}}

.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {accent} 0%, {accent_light} 100%) !important;
    border-color: {accent} !important;
    color: #ffffff !important;
}}

/* ─── INPUTS ─── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}}

[data-testid="stSelectbox"] > div > div {{
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}}

/* ─── TABS ─── */
[data-testid="stTabs"] > div > div > div > button {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748b !important;
    padding: 8px 16px !important;
}}

[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {{
    color: {accent} !important;
    border-bottom: 2px solid {accent} !important;
}}

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {{
    [data-testid="stSidebar"] {{
        width: 280px !important;
        min-width: 280px !important;
    }}
    .kpi-value {{ font-size: 22px !important; }}
    .kpi-card {{ padding: 14px 16px !important; }}
    div.stButton > button {{ width: 100% !important; }}
    [data-testid="stTabs"] > div > div > div > button {{ font-size: 12px !important; padding: 6px 10px !important; }}
    [data-testid="column"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 70px !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

def render_theme_toggle():
    """Simple theme toggle."""
    if "sidebar_light_mode" not in st.session_state:
        st.session_state.sidebar_light_mode = False
    
    is_light = st.session_state.sidebar_light_mode
    label = "☀️ Light" if not is_light else "🌙 Dark"
    
    if st.button(label, key="theme_toggle_sidebar", use_container_width=True):
        st.session_state.sidebar_light_mode = not is_light
        st.rerun()

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def render_page_header(title: str, subtitle: str = "", icon: str = "🌾"):
    """Render a styled page header."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%); 
                border-radius: 14px; padding: 24px 28px; margin-bottom: 20px; color: white;">
        <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
        <h2 style="margin: 0; font-size: clamp(18px, 3vw, 24px); font-weight: 700; color: white;">{title}</h2>
        {f'<p style="margin: 4px 0 0; opacity: 0.82; font-size: 13px; color: white;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, subtext: str = "", icon: str = ""):
    """Render a KPI card."""
    st.markdown(f"""
    <div class="kpi-card">
        {f'<div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>' if icon else ''}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-sub">{subtext}</div>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)

def render_alert(message: str, alert_type: str = "info"):
    """Render an alert box."""
    type_map = {
        "info": "alert-info",
        "success": "alert-success",
        "warning": "alert-warning",
        "error": "alert-danger"
    }
    st.markdown(f'<div class="alert-box {type_map.get(alert_type, "alert-info")}">{message}</div>', unsafe_allow_html=True)

def render_pill(text: str, pill_type: str = "neutral"):
    """Render a pill/badge."""
    st.markdown(f'<span class="pill pill-{pill_type}">{text}</span>', unsafe_allow_html=True)

def render_price(amount: float, currency: str = "ETB"):
    """Render a price."""
    st.markdown(f'<span class="price-tag">{currency} {amount:,.2f}</span>', unsafe_allow_html=True)

def render_section_title(title: str):
    """Render a section title."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
