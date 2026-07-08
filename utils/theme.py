"""
theme.py — Ethiopian AI Supply Chain Platform
Full dark/light theme support for both sidebar and main content
"""
import streamlit as st
from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════
# COLOUR TOKENS
# ═══════════════════════════════════════════════════════════════
DARK: Dict[str, str] = {
    "sidebar_bg": "#161b27",
    "sidebar_border": "#1e2a3a",
    "sidebar_text": "#e2e8f0",
    "sidebar_subtext": "#64748b",
    "sidebar_btn_bg": "#1e2a3a",
    "sidebar_btn_border": "#334155",
    "sidebar_btn_color": "#e2e8f0",
    "sidebar_divider": "#1e2a3a",
    "pill_bg": "#1e293b",
    "pill_color": "#94a3b8",
    "pill_border": "#334155",
    "main_bg": "#0f1117",
    "main_text": "#e2e8f0",
    "card_bg": "#161b27",
    "card_border": "#1e2a3a",
    "input_bg": "#1e2a3a",
    "input_border": "#334155",
    "input_text": "#e2e8f0",
}

LIGHT: Dict[str, str] = {
    "sidebar_bg": "#f8fafc",
    "sidebar_border": "#e2e8f0",
    "sidebar_text": "#1e293b",
    "sidebar_subtext": "#64748b",
    "sidebar_btn_bg": "#ffffff",
    "sidebar_btn_border": "#cbd5e1",
    "sidebar_btn_color": "#1e293b",
    "sidebar_divider": "#e2e8f0",
    "pill_bg": "#f1f5f9",
    "pill_color": "#475569",
    "pill_border": "#cbd5e1",
    "main_bg": "#f8fafc",
    "main_text": "#0f172a",
    "card_bg": "#ffffff",
    "card_border": "#e2e8f0",
    "input_bg": "#ffffff",
    "input_border": "#cbd5e1",
    "input_text": "#1e293b",
}

def _get_tokens() -> Dict[str, str]:
    return LIGHT if st.session_state.get("sidebar_light_mode", False) else DARK

# ═══════════════════════════════════════════════════════════════
# INJECT THEME CSS
# ═══════════════════════════════════════════════════════════════
def inject_theme():
    """Inject theme CSS for both sidebar and main content."""
    is_light = st.session_state.get("sidebar_light_mode", False)
    t = LIGHT if is_light else DARK
    accent = "#D4A017" if not is_light else "#1B4332"
    
    st.markdown(f"""
<style>
/* ─── BASE ─── */
html, body, [data-testid="stAppViewContainer"] {{
    background: {t["main_bg"]} !important;
    color: {t["main_text"]} !important;
    font-family: 'Inter', sans-serif;
}}

/* ─── SIDEBAR ─── */
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
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {accent}55 !important;
    color: {accent} !important;
}}

[data-testid="stSidebar"] hr {{
    border-color: {t["sidebar_divider"]} !important;
}}

[data-testid="stSidebar"] .stInfo {{
    background: {t["card_bg"]} !important;
    border-color: {t["card_border"]} !important;
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
.pill-neutral {{ background: {t["pill_bg"]}; color: {t["pill_color"]}; border: 1px solid {t["pill_border"]}; }}

/* ─── BUTTONS ─── */
.stButton > button {{
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    background: {t["input_bg"]} !important;
    border: 1px solid {t["input_border"]} !important;
    color: {t["input_text"]} !important;
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

/* ─── HIDE STREAMLIT BRANDING ─── */
#MainMenu, footer, header {{ visibility: hidden !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}

/* ─── INPUTS ─── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
    background: {t["input_bg"]} !important;
    border-color: {t["input_border"]} !important;
    color: {t["input_text"]} !important;
    border-radius: 8px !important;
}}

[data-testid="stSelectbox"] > div > div {{
    background: {t["input_bg"]} !important;
    border-color: {t["input_border"]} !important;
    color: {t["input_text"]} !important;
    border-radius: 8px !important;
}}

/* ─── TABS ─── */
[data-testid="stTabs"] > div > div > div > button {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {t["sidebar_subtext"]} !important;
}}

[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {{
    color: {accent} !important;
    border-bottom: 2px solid {accent} !important;
}}

/* ─── KPI CARDS ─── */
.kpi-card {{
    background: {t["card_bg"]} !important;
    border: 1px solid {t["card_border"]} !important;
    border-radius: 10px;
    padding: 20px 24px;
    height: 100%;
}}
.kpi-label {{ font-size: 11px; font-weight: 600; color: {t["sidebar_subtext"]} !important; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }}
.kpi-value {{ font-size: 28px; font-weight: 700; color: {t["main_text"]} !important; font-family: 'JetBrains Mono', monospace; line-height: 1; }}
.kpi-sub {{ font-size: 12px; color: {t["sidebar_subtext"]} !important; margin-top: 6px; }}

/* ─── ALERT BOXES ─── */
.alert-box {{ border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; border: 1px solid; }}
.alert-warning {{ background: #78350f22; border-color: #d9770666; color: #fbbf24; }}
.alert-danger {{ background: #7f1d1d22; border-color: #ef444466; color: #f87171; }}
.alert-info {{ background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }}
.alert-success {{ background: #14532d22; border-color: #16a34a66; color: #4ade80; }}

/* ─── SECTION TITLE ─── */
.section-title {{
    font-size: 13px;
    font-weight: 700;
    color: {t["sidebar_subtext"]} !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 24px 0 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid {t["card_border"]} !important;
}}

/* ─── PRICE TAG ─── */
.price-tag {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; color: {accent} !important; }}

/* ─── CONFIRM BOX ─── */
.confirm-box {{ background: #7f1d1d22; border: 1px solid #ef444455; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #fca5a5; margin-bottom: 8px; }}

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {{
    [data-testid="stSidebar"] {{ width: 280px !important; }}
    .kpi-value {{ font-size: 22px !important; }}
    .kpi-card {{ padding: 14px 16px !important; }}
    div.stButton > button {{ width: 100% !important; }}
    [data-testid="stTabs"] > div > div > div > button {{ font-size: 12px !important; padding: 6px 10px !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# THEME TOGGLE
# ═══════════════════════════════════════════════════════════════
def render_theme_toggle():
    """Render theme toggle button for sidebar."""
    if "sidebar_light_mode" not in st.session_state:
        st.session_state.sidebar_light_mode = False
    
    is_light = st.session_state.sidebar_light_mode
    label = "☀️ Light" if not is_light else "🌙 Dark"
    
    if st.button(label, key="theme_toggle_sidebar", use_container_width=True):
        st.session_state.sidebar_light_mode = not is_light
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def render_page_header(title: str, subtitle: str = "", icon: str = "🌾"):
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%); border-radius: 14px; padding: 24px 28px; margin-bottom: 20px; color: white;">
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
    type_map = {"info": "alert-info", "success": "alert-success", "warning": "alert-warning", "error": "alert-danger"}
    st.markdown(f'<div class="alert-box {type_map.get(alert_type, "alert-info")}">{message}</div>', unsafe_allow_html=True)

def render_pill(text: str, pill_type: str = "neutral"):
    st.markdown(f'<span class="pill pill-{pill_type}">{text}</span>', unsafe_allow_html=True)

def render_price(amount: float, currency: str = "ETB"):
    st.markdown(f'<span class="price-tag">{currency} {amount:,.2f}</span>', unsafe_allow_html=True)
