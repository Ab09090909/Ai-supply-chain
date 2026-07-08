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

LIGHT: Dict[str, str] = {
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

def _get_tokens() -> Dict[str, str]:
    """Get current theme tokens based on session state."""
    return LIGHT if st.session_state.get("sidebar_light_mode", False) else DARK

# ═══════════════════════════════════════════════════════════════
# CACHED CSS GENERATION
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def _generate_css(is_light: bool) -> str:
    """Generate CSS with caching for better performance."""
    t = LIGHT if is_light else DARK
    
    # Determine accent colors
    accent = "#D4A017" if not is_light else "#1B4332"
    accent_light = "#F4C430" if not is_light else "#2D6A4F"
    
    return f"""
<style>
/* ═══════════════════════════════════════════
   FONT IMPORTS
═══════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

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
    .admin-header {{ padding: 16px !important; flex-wrap: wrap; }}
    .admin-header h1 {{ font-size: 20px !important; }}
    .admin-badge {{ margin-left: 0 !important; }}
    [data-testid="stSidebar"] {{
        width: 280px !important;
    }}
}}

@media (min-width: 769px) and (max-width: 1024px) {{
    .dash-header h1 {{ font-size: 22px !important; }}
    .kpi-value {{ font-size: 24px !important; }}
}}

/* ═══════════════════════════════════════════
   SCROLLBAR STYLING
═══════════════════════════════════════════ */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: {t["card_bg"]};
}}
::-webkit-scrollbar-thumb {{
    background: {t["card_border"]};
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {t["input_border"]};
}}

/* ═══════════════════════════════════════════
   MAIN CONTENT — dynamic theme
═══════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"] {{
    background: {t["main_bg"]} !important;
    color: {t["main_text"]} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

[data-testid="stApp"] {{
    background: {t["main_bg"]} !important;
}}

/* Main content area */
[data-testid="stAppViewBlockContainer"] {{
    background: {t["main_bg"]} !important;
    padding-top: 1rem !important;
}}

/* Cards and containers */
.element-container, .stMarkdown, .stDataFrame, .stTable {{
    background: transparent !important;
}}

/* Headers */
h1, h2, h3, h4, h5, h6 {{
    color: {t["main_text"]} !important;
    font-weight: 600 !important;
}}

/* Paragraphs and captions */
p, .stCaption, .stMarkdown p {{
    color: {t["main_text"]} !important;
}}

/* Divider */
hr {{
    border-color: {t["card_border"]} !important;
    margin: 1rem 0 !important;
}}

/* Streamlit overrides */
[data-testid="stMetricValue"] {{
    color: {t["main_text"]} !important;
    font-weight: 700 !important;
}}

[data-testid="stMetricLabel"] {{
    color: {t["sidebar_subtext"]} !important;
    font-weight: 500 !important;
}}

[data-testid="stMetricDelta"] {{
    color: {t["sidebar_subtext"]} !important;
}}

/* Input fields */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {{
    background: {t["input_bg"]} !important;
    border-color: {t["input_border"]} !important;
    color: {t["input_text"]} !important;
    border-radius: 8px !important;
    transition: border-color 0.2s ease !important;
}}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stDateInput"] input:focus {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 2px {accent}33 !important;
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

/* Multi-select */
[data-testid="stMultiSelect"] > div > div {{
    background: {t["input_bg"]} !important;
    border-color: {t["input_border"]} !important;
    border-radius: 8px !important;
}}

/* ─────────────────────────────────────────────
   BUTTONS
──────────────────────────────────────────────── */
.stButton > button {{
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    background: {t["input_bg"]} !important;
    border: 1px solid {t["input_border"]} !important;
    color: {t["input_text"]} !important;
    cursor: pointer !important;
    padding: 0.5rem 1rem !important;
}}

.stButton > button:hover {{
    border-color: {accent}55 !important;
    color: {accent} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}}

.stButton > button:active {{
    transform: translateY(0) !important;
}}

.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {accent} 0%, {accent_light} 100%) !important;
    border-color: {accent} !important;
    color: #ffffff !important;
}}

.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 4px 16px {accent}44 !important;
    transform: translateY(-1px) !important;
}}

.stButton > button[kind="primary"]:active {{
    transform: translateY(0) !important;
}}

/* ─────────────────────────────────────────────
   SIDEBAR STYLES
──────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {t["sidebar_bg"]} !important;
    border-right: 1px solid {t["sidebar_border"]} !important;
    transition: all 0.3s ease !important;
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
    transition: all 0.15s ease !important;
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

/* ─────────────────────────────────────────────
   PILL STYLES
──────────────────────────────────────────────── */
.pill {{
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.3px;
    margin: 2px 0;
}}
.pill-success {{
    background: #14532d44;
    color: #4ade80;
    border: 1px solid #16a34a44;
}}
.pill-warning {{
    background: #78350f44;
    color: #fbbf24;
    border: 1px solid #d9770644;
}}
.pill-danger {{
    background: #7f1d1d44;
    color: #f87171;
    border: 1px solid #ef444444;
}}
.pill-info {{
    background: #1e3a5f44;
    color: #60a5fa;
    border: 1px solid #2563eb44;
}}
.pill-purple {{
    background: #3b1a6044;
    color: #a78bfa;
    border: 1px solid #7c3aed44;
}}
.pill-neutral {{
    background: {t["pill_bg"]};
    color: {t["pill_color"]};
    border: 1px solid {t["pill_border"]};
}}

/* ─────────────────────────────────────────────
   TABS
──────────────────────────────────────────────── */
[data-testid="stTabs"] > div > div > div > button {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {t["sidebar_subtext"]} !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
}}

[data-testid="stTabs"] > div > div > div > button:hover {{
    color: {t["main_text"]} !important;
}}

[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {{
    color: {accent} !important;
    border-bottom: 2px solid {accent} !important;
}}

/* ─────────────────────────────────────────────
   DATAFRAMES
──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 10px;
    overflow: hidden;
}}

[data-testid="stDataFrame"] table {{
    background: {t["card_bg"]} !important;
    color: {t["main_text"]} !important;
    width: 100% !important;
}}

[data-testid="stDataFrame"] th {{
    background: {t["card_border"]} !important;
    color: {t["main_text"]} !important;
    font-weight: 600 !important;
    padding: 8px 12px !important;
}}

[data-testid="stDataFrame"] td {{
    background: {t["card_bg"]} !important;
    color: {t["main_text"]} !important;
    padding: 8px 12px !important;
}}

[data-testid="stDataFrame"] tr:hover td {{
    background: {t["input_bg"]} !important;
}}

/* ─────────────────────────────────────────────
   METRICS
──────────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {t["card_bg"]} !important;
    border: 1px solid {t["card_border"]} !important;
    border-radius: 10px !important;
    padding: 16px !important;
    transition: all 0.2s ease !important;
}}

[data-testid="stMetric"]:hover {{
    border-color: {accent}55 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05) !important;
}}

/* ─────────────────────────────────────────────
   ALERTS
──────────────────────────────────────────────── */
.stAlert {{
    border-radius: 8px !important;
    border-left: 4px solid !important;
}}

.stAlert > div {{
    background: transparent !important;
}}

/* ─────────────────────────────────────────────
   HIDE STREAMLIT BRANDING
──────────────────────────────────────────────── */
#MainMenu, footer, header {{
    visibility: hidden !important;
}}
[data-testid="stToolbar"] {{
    display: none !important;
}}

/* ─────────────────────────────────────────────
   KPI CARDS
──────────────────────────────────────────────── */
.kpi-card {{
    background: {t["card_bg"]} !important;
    border: 1px solid {t["card_border"]} !important;
    border-radius: 10px;
    padding: 20px 24px;
    transition: all 0.2s ease;
    height: 100%;
}}

.kpi-card:hover {{
    border-color: {accent}55 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05) !important;
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
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    line-height: 1;
}}

.kpi-sub {{
    font-size: 12px;
    color: {t["sidebar_subtext"]} !important;
    margin-top: 6px;
}}

/* ─────────────────────────────────────────────
   SECTION TITLES
──────────────────────────────────────────────── */
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

/* ─────────────────────────────────────────────
   ALERT BOXES
──────────────────────────────────────────────── */
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
.alert-purple   {{ background: #3b1a6022; border-color: #7c3aed66; color: #a78bfa; }}

/* ─────────────────────────────────────────────
   PRICE TAG
──────────────────────────────────────────────── */
.price-tag {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 18px;
    font-weight: 700;
    color: {accent} !important;
}}

/* ─────────────────────────────────────────────
   DANGER BUTTON
──────────────────────────────────────────────── */
.danger-btn > button {{
    background: #7f1d1d44 !important;
    border: 1px solid #ef444455 !important;
    color: #f87171 !important;
}}

.danger-btn > button:hover {{
    background: #7f1d1d66 !important;
    border-color: #ef4444 !important;
}}

/* ─────────────────────────────────────────────
   CONFIRM BOX
──────────────────────────────────────────────── */
.confirm-box {{
    background: #7f1d1d22;
    border: 1px solid #ef444455;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: #fca5a5;
    margin-bottom: 8px;
}}

/* ─────────────────────────────────────────────
   MATCH BAR
──────────────────────────────────────────────── */
.match-bar-bg {{ background: {t["card_border"]}; border-radius: 4px; height: 6px; margin-top: 6px; overflow: hidden; }}
.match-bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.4s ease; }}

/* ─────────────────────────────────────────────
   STATUS TRACKER
──────────────────────────────────────────────── */
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
    background: {t["card_border"]};
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
.track-label {{ font-size: 10px; color: {t["sidebar_subtext"]}; }}

/* ─────────────────────────────────────────────
   ADMIN HEADER
──────────────────────────────────────────────── */
.admin-header {{
    background: linear-gradient(135deg, #1a2744 0%, #0f172a 60%, #162032 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
}}
.admin-header-icon {{ font-size: 40px; line-height: 1; }}
.admin-header h1 {{
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.3px;
}}
.admin-header p {{
    margin: 4px 0 0;
    font-size: 13px;
    color: #64748b;
}}
.admin-badge {{
    margin-left: auto;
    background: #1e3a5f;
    border: 1px solid #2563eb44;
    color: #60a5fa;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* ─────────────────────────────────────────────
   DASH HEADER
──────────────────────────────────────────────── */
.dash-header {{
    background: linear-gradient(135deg, #1a1020 0%, #0f1117 60%, #1a1030 100%);
    border: 1px solid #2a1a4a;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
}}
.dash-header-icon {{ font-size: 40px; line-height: 1; }}
.dash-header h1 {{
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.3px;
}}
.dash-header p {{
    margin: 4px 0 0;
    font-size: 13px;
    color: #64748b;
}}
.dash-badge {{
    margin-left: auto;
    background: #3b1a6044;
    border: 1px solid #7c3aed44;
    color: #a78bfa;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* ─────────────────────────────────────────────
   FRAUD RISK BADGES
──────────────────────────────────────────────── */
.fraud-low  {{ color: #4ade80; font-weight: 600; font-size: 12px; }}
.fraud-med  {{ color: #fbbf24; font-weight: 600; font-size: 12px; }}
.fraud-high {{ color: #f87171; font-weight: 600; font-size: 12px; }}

/* ─────────────────────────────────────────────
   ACTIVITY FEED
──────────────────────────────────────────────── */
.activity-item {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid {t["card_border"]};
}}
.activity-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}}
.activity-text {{ font-size: 13px; color: {t["main_text"]}; }}
.activity-time {{ font-size: 11px; color: {t["sidebar_subtext"]}; margin-top: 2px; }}

/* ─────────────────────────────────────────────
   RECORD CARDS
──────────────────────────────────────────────── */
.record-card {{
    background: {t["card_bg"]};
    border: 1px solid {t["card_border"]};
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: all 0.15s ease;
}}
.record-card:hover {{ border-color: {accent}55; }}
.record-name {{
    font-size: 15px;
    font-weight: 600;
    color: {t["main_text"]};
    margin: 0 0 4px;
}}
.record-meta {{
    font-size: 12px;
    color: {t["sidebar_subtext"]};
    margin: 0;
}}

/* ─────────────────────────────────────────────
   FORECAST CONTAINER
──────────────────────────────────────────────── */
.forecast-container {{
    background: {t["card_bg"]};
    border: 1px solid {t["card_border"]};
    border-radius: 10px;
    padding: 20px;
    margin-top: 16px;
}}

/* ─────────────────────────────────────────────
   DOCUMENT PREVIEW
──────────────────────────────────────────────── */
.doc-preview-container {{
    background: {t["card_bg"]};
    border: 1px solid {t["card_border"]};
    border-radius: 12px;
    padding: 20px;
    margin-top: 12px;
}}

/* ─────────────────────────────────────────────
   PRODUCT IMAGE CONTAINER
──────────────────────────────────────────────── */
.product-img-container {{
    background: {t["input_bg"]};
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 120px;
    border: 1px solid {t["card_border"]};
}}
.product-img-container img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}

/* ─────────────────────────────────────────────
   PROFILE EDITOR MODAL
──────────────────────────────────────────────── */
.profile-editor-modal {{
    background: {t["card_bg"]} !important;
    border: 1px solid {t["card_border"]} !important;
    border-radius: 16px;
    padding: 30px;
    margin: 20px 0;
    max-height: 90vh;
    overflow-y: auto;
}}
.profile-pic-upload {{
    text-align: center;
    margin: 20px 0;
}}
@media (max-width: 768px) {{
    .profile-editor-modal {{
        padding: 16px;
        margin: 10px 0;
        max-height: 95vh;
    }}
}}

/* ─────────────────────────────────────────────
   SKELETON LOADING
──────────────────────────────────────────────── */
@keyframes shimmer {{
    0% {{ background-position: -200% 0; }}
    100% {{ background-position: 200% 0; }}
}}
.skeleton {{
    background: linear-gradient(90deg, {t["card_border"]} 25%, {t["input_bg"]} 50%, {t["card_border"]} 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
}}

/* ─────────────────────────────────────────────
   TOAST/NOTIFICATION STYLES
──────────────────────────────────────────────── */
.stToast {{
    border-radius: 10px !important;
    border-left: 4px solid {accent} !important;
}}
</style>
"""

# ═══════════════════════════════════════════════════════════════
# INJECT GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
def inject_theme():
    """Call near the top of each page. Applies to both sidebar and main content."""
    is_light = st.session_state.get("sidebar_light_mode", False)
    css = _generate_css(is_light)
    st.markdown(css, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# THEME TOGGLE WIDGET
# ═══════════════════════════════════════════════════════════════
def render_theme_toggle():
    """Render a simple theme toggle button for sidebar."""
    if "sidebar_light_mode" not in st.session_state:
        st.session_state.sidebar_light_mode = False
    
    is_light = st.session_state.sidebar_light_mode
    label = "☀️ Light Theme" if not is_light else "🌙 Dark Theme"
    
    if st.button(label, key="theme_toggle_sidebar", use_container_width=True):
        st.session_state.sidebar_light_mode = not is_light
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# PAGE HEADER HELPERS
# ═══════════════════════════════════════════════════════════════
def render_page_header(title: str, subtitle: str = "", icon: str = "🌾"):
    """Render a styled page header with icon and subtitle."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        border-radius: 14px; 
        padding: 28px 32px; 
        margin-bottom: 24px; 
        color: white;
    ">
        <div style="font-size: 36px; margin-bottom: 10px;">{icon}</div>
        <h2 style="margin: 0; font-size: clamp(18px, 3vw, 26px); font-weight: 700; color: white;">
            {title}
        </h2>
        {f'<p style="margin: 6px 0 0; opacity: 0.82; font-size: 14px; color: white;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, subtext: str = "", icon: str = ""):
    """Render a KPI card with consistent styling."""
    st.markdown(f"""
    <div class="kpi-card">
        {f'<div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>' if icon else ''}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-sub">{subtext}</div>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)

def render_section_title(title: str):
    """Render a section title with consistent styling."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def render_alert(message: str, alert_type: str = "info"):
    """Render an alert box with consistent styling."""
    type_map = {
        "info": "alert-info",
        "success": "alert-success",
        "warning": "alert-warning",
        "error": "alert-danger"
    }
    css_class = type_map.get(alert_type, "alert-info")
    st.markdown(f'<div class="alert-box {css_class}">{message}</div>', unsafe_allow_html=True)

def render_pill(text: str, pill_type: str = "neutral"):
    """Render a pill/badge with consistent styling."""
    st.markdown(f'<span class="pill pill-{pill_type}">{text}</span>', unsafe_allow_html=True)

def render_price(amount: float, currency: str = "ETB"):
    """Render a price with consistent styling."""
    st.markdown(f'<span class="price-tag">{currency} {amount:,.2f}</span>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# THEME UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def get_current_theme() -> str:
    """Get the current theme name."""
    return "light" if st.session_state.get("sidebar_light_mode", False) else "dark"

def is_dark_mode() -> bool:
    """Check if dark mode is active."""
    return not st.session_state.get("sidebar_light_mode", False)

def is_light_mode() -> bool:
    """Check if light mode is active."""
    return st.session_state.get("sidebar_light_mode", False)

def get_accent_color() -> str:
    """Get the current accent color based on theme."""
    is_light = st.session_state.get("sidebar_light_mode", False)
    return "#D4A017" if not is_light else "#1B4332"

def get_text_color() -> str:
    """Get the current text color based on theme."""
    t = _get_tokens()
    return t["main_text"]

def get_background_color() -> str:
    """Get the current background color based on theme."""
    t = _get_tokens()
    return t["main_bg"]

# ═══════════════════════════════════════════════════════════════
# RESPONSIVE UTILITY
# ═══════════════════════════════════════════════════════════════
def responsive_columns(cols: int) -> list:
    """
    Create responsive columns that stack on mobile.
    
    Args:
        cols: Number of columns to create
    
    Returns:
        List of column objects
    """
    return st.columns(cols)

def mobile_responsive_container(use_container_width: bool = True) -> st.container:
    """Create a container with mobile-responsive styling."""
    return st.container()
