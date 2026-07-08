"""
theme.py — Minimal theme for sidebar
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

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {{
    background: #161b27 !important;
    border-right: 1px solid #1e2a3a !important;
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
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {accent}55 !important;
    color: {accent} !important;
}}

[data-testid="stSidebar"] hr {{
    border-color: #1e2a3a !important;
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

/* ─── HIDE STREAMLIT BRANDING ─── */
#MainMenu, footer, header {{ visibility: hidden !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}

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

[data-testid="stSelectbox"] option {{
    background: #1e2a3a !important;
    color: #e2e8f0 !important;
}}

/* ─── TABS ─── */
[data-testid="stTabs"] > div > div > div > button {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748b !important;
    padding: 8px 16px !important;
}}

[data-testid="stTabs"] > div > div > div > button:hover {{
    color: #e2e8f0 !important;
}}

[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {{
    color: {accent} !important;
    border-bottom: 2px solid {accent} !important;
}}

/* ─── KPI CARDS ─── */
.kpi-card {{
    background: #161b27 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 10px;
    padding: 20px 24px;
    height: 100%;
}}
.kpi-label {{ font-size: 11px; font-weight: 600; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }}
.kpi-value {{ font-size: 28px; font-weight: 700; color: #f1f5f9 !important; font-family: 'JetBrains Mono', monospace; line-height: 1; }}
.kpi-sub {{ font-size: 12px; color: #64748b !important; margin-top: 6px; }}

/* ─── SECTION TITLE ─── */
.section-title {{
    font-size: 13px;
    font-weight: 700;
    color: #475569 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 24px 0 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2a3a;
}}

/* ─── PRICE TAG ─── */
.price-tag {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; color: {accent} !important; }}

/* ─── ALERT BOXES ─── */
.alert-box {{ border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; border: 1px solid; }}
.alert-warning {{ background: #78350f22; border-color: #d9770666; color: #fbbf24; }}
.alert-danger {{ background: #7f1d1d22; border-color: #ef444466; color: #f87171; }}
.alert-info {{ background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }}
.alert-success {{ background: #14532d22; border-color: #16a34a66; color: #4ade80; }}
.alert-purple {{ background: #3b1a6022; border-color: #7c3aed66; color: #a78bfa; }}

/* ─── CONFIRM BOX ─── */
.confirm-box {{ background: #7f1d1d22; border: 1px solid #ef444455; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #fca5a5; margin-bottom: 8px; }}

/* ─── DANGER BUTTON ─── */
.danger-btn > button {{
    background: #7f1d1d44 !important;
    border: 1px solid #ef444455 !important;
    color: #f87171 !important;
}}

/* ─── RECORD CARDS ─── */
.record-card {{
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.15s;
}}
.record-card:hover {{ border-color: {accent}55; }}

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {{
    [data-testid="stSidebar"] {{ width: 280px !important; }}
    .kpi-value {{ font-size: 22px !important; }}
    .kpi-card {{ padding: 14px 16px !important; }}
    div.stButton > button {{ width: 100% !important; }}
    [data-testid="stTabs"] > div > div > div > button {{ font-size: 12px !important; padding: 6px 10px !important; }}
    [data-testid="column"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
}}

/* ─── ACTIVITY FEED ─── */
.activity-item {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #1e2a3a;
}}
.activity-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}}
.activity-text {{ font-size: 13px; color: #94a3b8; }}
.activity-time {{ font-size: 11px; color: #475569; margin-top: 2px; }}

/* ─── STATUS TRACKER ─── */
.status-track {{
    display: flex;
    align-items: center;
    gap: 0;
    margin: 12px 0;
}}
.track-step {{
    flex: 1;
    text-align: center;
    position: relative;
}}
.track-step::after {{
    content: '';
    position: absolute;
    top: 10px;
    right: -50%;
    width: 100%;
    height: 2px;
    background: #1e2a3a;
    z-index: 0;
}}
.track-step:last-child::after {{ display: none; }}
.track-dot {{
    width: 20px;
    height: 20px;
    border-radius: 50%;
    margin: 0 auto 4px;
    position: relative;
    z-index: 1;
}}
.track-label {{ font-size: 10px; color: #475569; }}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #0f1117; }}
::-webkit-scrollbar-thumb {{ background: #1e2a3a; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: #334155; }}
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

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
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
