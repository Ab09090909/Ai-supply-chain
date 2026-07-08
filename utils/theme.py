"""
theme.py — Minimal theme for app
"""
import streamlit as st

def inject_theme():
    """Inject minimal theme CSS."""
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

/* ─── HIDE SIDEBAR ─── */
[data-testid="stSidebar"] {{
    display: none !important;
}}

[data-testid="collapsedControl"] {{
    display: none !important;
}}

#MainMenu, footer, header {{
    visibility: hidden !important;
}}
[data-testid="stToolbar"] {{
    display: none !important;
}}

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
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 70px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }}
    [data-testid="stTabs"] > div > div > div > button {{
        font-size: 12px !important;
        padding: 6px 10px !important;
        white-space: nowrap !important;
    }}
    [data-testid="stTabs"] > div > div {{
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }}
}}

@media (min-width: 769px) {{
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 80px !important;
        padding-left: 24px !important;
        padding-right: 24px !important;
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
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%); 
                border-radius: 14px; padding: 24px 28px; margin-bottom: 20px; color: white;">
        <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
        <h2 style="margin: 0; font-size: clamp(18px, 3vw, 24px); font-weight: 700; color: white;">{title}</h2>
        {f'<p style="margin: 4px 0 0; opacity: 0.82; font-size: 13px; color: white;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, subtext: str = "", icon: str = ""):
    st.markdown(f"""
    <div class="kpi-card">
        {f'<div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>' if icon else ''}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-sub">{subtext}</div>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)

def render_alert(message: str, alert_type: str = "info"):
    type_map = {
        "info": "alert-info",
        "success": "alert-success",
        "warning": "alert-warning",
        "error": "alert-danger"
    }
    st.markdown(f'<div class="alert-box {type_map.get(alert_type, "alert-info")}">{message}</div>', unsafe_allow_html=True)

def render_pill(text: str, pill_type: str = "neutral"):
    st.markdown(f'<span class="pill pill-{pill_type}">{text}</span>', unsafe_allow_html=True)

def render_price(amount: float, currency: str = "ETB"):
    st.markdown(f'<span class="price-tag">{currency} {amount:,.2f}</span>', unsafe_allow_html=True)

def render_section_title(title: str):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
