"""
theme.py — Ethiopian AI Supply Chain Platform
Full dark/light theme support for both sidebar and main content
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
    # Main content colors
    "main_bg":            "#0f1117",
    "main_text":          "#e2e8f0",
    "card_bg":            "#161b27",
    "card_border":        "#1e2a3a",
    "input_bg":           "#1e2a3a",
    "input_border":       "#334155",
    "input_text":         "#e2e8f0",
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
    # Main content colors
    "main_bg":            "#f8fafc",
    "main_text":          "#0f172a",
    "card_bg":            "#ffffff",
    "card_border":        "#e2e8f0",
    "input_bg":           "#ffffff",
    "input_border":       "#cbd5e1",
    "input_text":         "#1e293b",
}

def _get_tokens() -> dict:
    return LIGHT if st.session_state.get("sidebar_light_mode", False) else DARK

# ═══════════════════════════════════════════════════════════════
# INJECT GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
def inject_theme():
    """Call near the top of each page. Applies to both sidebar and main content."""
    t = _get_tokens()
    is_light = st.session_state.get("sidebar_light_mode", False)
    
    # Determine accent colors based on theme
    accent = "#D4A017" if not is_light else "#1B4332"
    accent_light = "#F4C430" if not is_light else "#2D6A4F"
    
    st.markdown(f"""
<style>
/* ═══════════════════════════════════════════
   RESPONSIVE UTILITIES
═══════════════════════════════════════════ */
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
}}

@media (min-width: 769px) and (max-width: 1024px) {{
    .dash-header h1 {{ font-size: 22px !important; }}
    .kpi-value {{ font-size: 24px !important; }}
}}

/* ═══════════════════════════════════════════
   MAIN CONTENT — dynamic theme
═══════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"] {{
    background: {t["main_bg"]} !important;
    color: {t["main_text"]} !important;
    font-family: 'Inter', sans-serif;
}}

[data-testid="stApp"] {{
    background: {t["main_bg"]} !important;
}}

/* Main content area */
[data-testid="stAppViewBlockContainer"] {{
    background: {t["main_bg"]} !important;
}}

/* Cards and containers */
.element-container, .stMarkdown, .stDataFrame, .stTable {{
    background: transparent !important;
}}

/* Headers */
h1, h2, h3, h4, h5, h6 {{
    color: {t["main_text"]} !important;
}}

/* Paragraphs and captions */
p, .stCaption, .stMarkdown p {{
    color: {t["main_text"]} !important;
}}

/* Divider */
hr {{
    border-color: {t["card_border"]} !important;
}}

/* ── Streamlit overrides ── */
[data-testid="stMetricValue"] {{
    color: {t["main_text"]} !important;
}}

[data-testid="stMetricLabel"] {{
    color: {t["sidebar_subtext"]} !important;
}}

/* ── Input fields ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {{
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

[data-testid="stSelectbox"] option {{
    background: {t["input_bg"]} !important;
    color: {t["input_text"]} !important;
}}

/* ── Buttons ── */
.stButton > button {{
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    background: {t["input_bg"]} !important;
    border: 1px solid {t["input_border"]} !important;
    color: {t["input_text"]} !important;
}}

.stButton > button:hover {{
    border-color: {accent}55 !important;
    color: {accent} !important;
}}

.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {accent} 0%, {accent_light} 100%) !important;
    border-color: {accent} !important;
    color: #fff !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] > div > div > div > button {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {t["sidebar_subtext"]} !important;
}}

[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {{
    color: {accent} !important;
    border-bottom-color: {accent} !important;
}}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {{
    border-radius: 10px;
    overflow: hidden;
}}

[data-testid="stDataFrame"] table {{
    background: {t["card_bg"]} !important;
    color: {t["main_text"]} !important;
}}

[data-testid="stDataFrame"] th {{
    background: {t["card_border"]} !important;
    color: {t["main_text"]} !important;
}}

[data-testid="stDataFrame"] td {{
    background: {t["card_bg"]} !important;
    color: {t["main_text"]} !important;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background: {t["card_bg"]} !important;
    border: 1px solid {t["card_border"]} !important;
    border-radius: 10px !important;
    padding: 16px !important;
}}

/* ── Info/Warning/Success boxes ── */
.stAlert {{
    border-radius: 8px !important;
}}

/* ── Sidebar ── */
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

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── KPI Cards ── */
.kpi-card {{
    background: {t["card_bg"]} !important;
    border: 1px solid {t["card_border"]} !important;
    border-radius: 10px;
    padding: 20px 24px;
    transition: border-color 0.2s;
    height: 100%;
}}

.kpi-card:hover {{
    border-color: {accent}55 !important;
}}

.kpi-label {{
    font-size: 11px;
    font-weight: 600;
    color: {t["sidebar_subtext"]} !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}}

.kpi-value {{
    font-size: 28px;
    font-weight: 700;
    color: {t["main_text"]} !important;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}}

.kpi-sub {{
    font-size: 12px;
    color: {t["sidebar_subtext"]} !important;
    margin-top: 6px;
}}

/* ── Section Titles ── */
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

/* ── Alert boxes ── */
.alert-box {{
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    margin-bottom: 12px;
    border: 1px solid;
}}
.alert-warning {{ background: #78350f22; border-color: #d9770666; color: #fbbf24; }}
.alert-danger   {{ background: #7f1d1d22; border-color: #ef444466; color: #f87171; }}
.alert-info     {{ background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }}
.alert-success  {{ background: #14532d22; border-color: #16a34a66; color: #4ade80; }}

/* ── Price tag ── */
.price-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: {accent} !important;
}}

/* ── Danger button ── */
.danger-btn > button {{
    background: #7f1d1d44 !important;
    border: 1px solid #ef444455 !important;
    color: #f87171 !important;
}}

/* ── Confirm box ── */
.confirm-box {{
    background: #7f1d1d22;
    border: 1px solid #ef444455;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: #fca5a5;
    margin-bottom: 8px;
}}

/* ── Pill styles ── */
.pill {{
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.3px;
}}
.pill-success {{ background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }}
.pill-warning {{ background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }}
.pill-danger  {{ background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }}
.pill-info    {{ background: #1e3a5f44; color: #60a5fa; border: 1px solid
