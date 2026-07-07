"""Modern Ethiopian-inspired theme with dark/light toggle support."""
import streamlit as st

# ─────────────────────────────────────────────
# Theme Color Palettes
# ─────────────────────────────────────────────
THEME = {
    "primary":          "#1B4332",
    "primary_light":    "#2D6A4F",
    "primary_lighter":  "#40916C",
    "accent":           "#D4A017",
    "accent_light":     "#F4C430",
    "success":          "#10B981",
    "warning":          "#F59E0B",
    "danger":           "#EF4444",
    "info":             "#3B82F6",
    "dark":             "#1F2937",
    "gray":             "#6B7280",
    "light":            "#F9FAFB",
    "white":            "#FFFFFF",
}

# ─────────────────────────────────────────────
# Light Theme CSS (Ethiopian-inspired)
# ─────────────────────────────────────────────
LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%) !important;
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

# ─────────────────────────────────────────────
# Dark Theme CSS (Professional dark design)
# ────────────────────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif !important;
    background: #0f1117 !important;
    color: #e2e8f0 !important;
}
header[data-testid="stHeader"] {
    background: rgba(15,17,23,0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

section[data-testid="stSidebar"] {
    background: #161b27 !important;
    color: #e2e8f0 !important;
    border-right: 1px solid #1e2a3a !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #1e2a3a !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
    padding: 10px 16px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2563eb22 !important;
    border-color: #2563eb !important;
    color: #60a5fa !important;
}

[data-testid="stContainer"] {
    background: #161b27;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #1e2a3a;
    margin-bottom: 14px;
}

[data-testid="stMetric"] {
    background: #161b27;
    border-radius: 10px;
    padding: 18px;
    border: 1px solid #1e2a3a;
}
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 700 !important; font-size: 26px !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; font-size: 11px !important; }

.stButton > button {
    background: #1e2a3a !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    border-color: #60a5fa55 !important;
    color: #60a5fa !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%) !important;
    border-color: #2563eb !important;
    color: #fff !important;
    font-weight: 600 !important;
}

h1, h2, h3 { color: #f1f5f9 !important; font-weight: 700 !important; }
p, span, div { color: #e2e8f0; }

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #1e2a3a !important;
    border-color: #334155 !important;
    border-radius: 8px !important;
}

#MainMenu, footer { visibility: hidden; }
</style>
"""

# ─────────────────────────────────────────────
# Theme Toggle CSS (for the toggle buttons)
# ─────────────────────────────────────────────
TOGGLE_CSS = """
<style>
.theme-toggle-container {
    display: flex;
    gap: 6px;
    margin: 8px 0;
}
.theme-toggle-btn {
    flex: 1;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #334155;
    background: #1e2a3a;
    color: #94a3b8;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}
.theme-toggle-btn:hover {
    border-color: #60a5fa;
    color: #60a5fa;
}
.theme-toggle-btn.active {
    background: #2563eb;
    border-color: #2563eb;
    color: white;
}
</style>
"""


# ─────────────────────────────────────────────
# Core Functions
# ─────────────────────────────────────────────
def inject_theme():
    """Inject theme based on user preference (dark by default)."""
    # Initialize theme mode in session state
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    
    # Inject appropriate CSS
    if st.session_state.theme_mode == "light":
        st.markdown(LIGHT_CSS, unsafe_allow_html=True)
    else:
        st.markdown(DARK_CSS, unsafe_allow_html=True)
    
    # Mark as injected
    st.session_state.theme_injected = True


def toggle_theme():
    """Toggle between dark and light mode."""
    current = st.session_state.get("theme_mode", "dark")
    st.session_state.theme_mode = "light" if current == "dark" else "dark"
    # Clear the injected flag so CSS re-injects on next run
    st.session_state.pop("theme_injected", None)


def render_theme_toggle():
    """Render a theme toggle UI in the sidebar."""
    st.markdown(TOGGLE_CSS, unsafe_allow_html=True)
    
    current = st.session_state.get("theme_mode", "dark")
    
    col1, col2 = st.columns(2)
    with col1:
        is_dark_active = current == "dark"
        btn_style_dark = "theme-toggle-btn active" if is_dark_active else "theme-toggle-btn"
        if st.button("🌙 Dark", key="theme_toggle_dark", use_container_width=True):
            if current != "dark":
                st.session_state.theme_mode = "dark"
                st.session_state.pop("theme_injected", None)
                st.rerun()
    
    with col2:
        is_light_active = current == "light"
        btn_style_light = "theme-toggle-btn active" if is_light_active else "theme-toggle-btn"
        if st.button("☀️ Light", key="theme_toggle_light", use_container_width=True):
            if current != "light":
                st.session_state.theme_mode = "light"
                st.session_state.pop("theme_injected", None)
                st.rerun()


def render_page_header(icon, title, subtitle):
    """Modern page header used on every dashboard."""
    mode = st.session_state.get("theme_mode", "dark")
    
    if mode == "light":
        bg = "linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%)"
        color = "white"
    else:
        bg = "linear-gradient(135deg, #1a2744 0%, #0f172a 60%, #162032 100%)"
        color = "#f1f5f9"
    
    st.markdown(f"""
    <div style="background: {bg};
                border-radius: 16px;
                padding: 28px;
                color: {color};
                margin-bottom: 20px;
                border: 1px solid #1e3a5f;">
        <h1 style="color: {color}; margin: 0;">{icon} {title}</h1>
        <p style="opacity: 0.9; margin: 6px 0 0 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
