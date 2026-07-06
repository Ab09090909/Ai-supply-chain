"""Modern Ethiopian-inspired theme."""
import streamlit as st

THEME = {
    "primary": "#1B4332",
    "primary_light": "#2D6A4F",
    "primary_lighter": "#40916C",
    "accent": "#D4A017",
    "accent_light": "#F4C430",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#3B82F6",
    "dark": "#1F2937",
    "gray": "#6B7280",
    "light": "#F9FAFB",
    "white": "#FFFFFF",
}

MODERN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%);
}
header[data-testid="stHeader"] {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 8px rgba(27,67,50,0.08);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 100%) !important;
    color: white !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: white !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
    transition: all 0.25s ease !important;
    text-align: left !important;
    padding: 10px 16px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(212,160,23,0.25) !important;
    border-color: #F4C430 !important;
    transform: translateX(4px) !important;
}

[data-testid="stContainer"] {
    background: white;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(27,67,50,0.06);
    border: 1px solid rgba(27,67,50,0.08);
    margin-bottom: 14px;
}

[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    border-left: 4px solid #1B4332;
}
[data-testid="stMetricValue"] { color: #1B4332 !important; font-weight: 700 !important; font-size: 26px !important; }
[data-testid="stMetricLabel"] { color: #6B7280 !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; font-size: 11px !important; }

.stButton > button {
    background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2D6A4F 0%, #40916C 100%) !important;
    transform: translateY(-2px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #D4A017 0%, #F4C430 100%) !important;
    color: #1B4332 !important;
    font-weight: 700 !important;
}

h1, h2, h3 { color: #1B4332 !important; font-weight: 700 !important; }
#MainMenu, footer { visibility: hidden; }
</style>
"""


def inject_theme():
    """Inject theme once per session."""
    if "theme_injected" not in st.session_state:
        st.markdown(MODERN_CSS, unsafe_allow_html=True)
        st.session_state.theme_injected = True


def render_page_header(icon, title, subtitle):
    """Modern page header used on every dashboard."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
                border-radius: 16px; padding: 28px; color: white; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">{icon} {title}</h1>
        <p style="opacity: 0.9; margin: 6px 0 0 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
