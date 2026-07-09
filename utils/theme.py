"""
theme.py — Global dark theme + reusable UI helpers
"""
import streamlit as st


def inject_theme():
    """Inject the global dark theme CSS into the current page."""
    is_light = st.session_state.get("sidebar_light_mode", False)
    accent       = "#D4A017" if not is_light else "#1B4332"
    accent_light = "#F4C430" if not is_light else "#2D6A4F"

    st.markdown(f"""
<style>
/* ─── BASE ─── */
html, body, [data-testid="stAppViewContainer"] {{
    background: #0f1117 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif;
}}

/* ─── HIDE DEFAULT SIDEBAR & BRANDING ─── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
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
    color: #1B4332 !important;
    font-weight: 600 !important;
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

/* ─── KPI CARDS ─── */
.kpi-card {{
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-color 0.15s;
}}
.kpi-card:hover {{
    border-color: {accent}44;
}}
.kpi-label {{
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 26px;
    font-weight: 700;
    color: {accent};
    line-height: 1.1;
}}
.kpi-sub {{
    font-size: 12px;
    color: #94a3b8;
    margin-top: 4px;
}}

/* ─── ALERT BOXES ─── */
.alert-box {{
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    margin: 8px 0;
    line-height: 1.5;
}}
.alert-info    {{ background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }}
.alert-success {{ background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }}
.alert-warning {{ background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }}
.alert-danger  {{ background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }}

/* ─── PILLS ─── */
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
.pill-danger  {{ background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }}
.pill-info    {{ background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }}
.pill-neutral {{ background: #1e293b;   color: #94a3b8; border: 1px solid #334155;   }}

/* ─── PRICE TAG ─── */
.price-tag {{
    font-size: 18px;
    font-weight: 700;
    color: {accent};
    font-variant-numeric: tabular-nums;
}}

/* ─── SECTION TITLE ─── */
.section-title {{
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 16px 0 8px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2a3a;
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
    div.stButton > button {{
        width: 100% !important;
    }}
    .kpi-value {{
        font-size: 22px;
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
    """Render a light/dark mode toggle button."""
    if "sidebar_light_mode" not in st.session_state:
        st.session_state.sidebar_light_mode = False

    is_light = st.session_state.sidebar_light_mode
    label = "☀️ Light" if not is_light else "🌙 Dark"

    if st.button(label, key="theme_toggle_sidebar", use_container_width=True):
        st.session_state.sidebar_light_mode = not is_light
        st.rerun()


def render_page_header(title: str, subtitle: str = "", icon: str = "🌾"):
    """Render a full-width gradient page header."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
                border-radius: 14px; padding: 24px 28px; margin-bottom: 20px; color: white;">
        <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
        <h2 style="margin: 0; font-size: clamp(18px, 3vw, 24px); font-weight: 700; color: white;">{title}</h2>
        {f'<p style="margin: 4px 0 0; opacity: 0.82; font-size: 13px; color: white;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, subtext: str = "", icon: str = ""):
    """Render a KPI metric card."""
    st.markdown(f"""
    <div class="kpi-card">
        {f'<div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>' if icon else ''}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-sub">{subtext}</div>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)


def render_alert(message: str, alert_type: str = "info"):
    """Render a styled alert box. alert_type: info | success | warning | error"""
    type_map = {
        "info":    "alert-info",
        "success": "alert-success",
        "warning": "alert-warning",
        "error":   "alert-danger",
    }
    css_class = type_map.get(alert_type, "alert-info")
    st.markdown(f'<div class="alert-box {css_class}">{message}</div>', unsafe_allow_html=True)


def render_pill(text: str, pill_type: str = "neutral"):
    """Render an inline status pill. pill_type: success | warning | danger | info | neutral"""
    st.markdown(f'<span class="pill pill-{pill_type}">{text}</span>', unsafe_allow_html=True)


def render_price(amount: float, currency: str = "ETB"):
    """Render a formatted price with accent styling."""
    st.markdown(f'<span class="price-tag">{currency} {amount:,.2f}</span>', unsafe_allow_html=True)


def render_section_title(title: str):
    """Render a subtle section divider with title."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
