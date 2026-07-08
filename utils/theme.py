"""
theme.py — Ethiopian AI Supply Chain Platform
Handles:
  - Dark / Light toggle that ONLY changes the sidebar
  - Responsive CSS for mobile and desktop
  - inject_theme() called once per page
  - render_theme_toggle() placed inside each sidebar
"""
import streamlit as st


# ══════════════════════════════════════════════════════════════
#  COLOUR TOKENS
# ══════════════════════════════════════════════════════════════
DARK = {
    "sidebar_bg":        "#161b27",
    "sidebar_border":    "#1e2a3a",
    "sidebar_text":      "#e2e8f0",
    "sidebar_subtext":   "#64748b",
    "sidebar_btn_bg":    "#1e2a3a",
    "sidebar_btn_border":"#334155",
    "sidebar_btn_color": "#e2e8f0",
    "sidebar_divider":   "#1e2a3a",
    "pill_bg":           "#1e293b",
    "pill_color":        "#94a3b8",
    "pill_border":       "#334155",
}

LIGHT = {
    "sidebar_bg":        "#f8fafc",
    "sidebar_border":    "#e2e8f0",
    "sidebar_text":      "#1e293b",
    "sidebar_subtext":   "#64748b",
    "sidebar_btn_bg":    "#ffffff",
    "sidebar_btn_border":"#cbd5e1",
    "sidebar_btn_color": "#1e293b",
    "sidebar_divider":   "#e2e8f0",
    "pill_bg":           "#f1f5f9",
    "pill_color":        "#475569",
    "pill_border":       "#cbd5e1",
}


def _get_tokens() -> dict:
    return LIGHT if st.session_state.get("sidebar_light_mode") else DARK


# ══════════════════════════════════════════════════════════════
#  INJECT GLOBAL CSS  (main content always dark + responsive)
# ══════════════════════════════════════════════════════════════
def inject_theme():
    """
    Call near the top of each page (after set_page_config).
    Safe to call multiple times — each call re-injects the latest tokens.
    Injects:
      1. Responsive CSS (mobile ≤768 px / desktop > 768 px)
      2. Sidebar-only theming based on sidebar_light_mode session state
    Main content area is ALWAYS dark — never changes.
    """
    t = _get_tokens()

    st.markdown(f"""
<style>
/* ═══════════════════════════════════════════
   RESPONSIVE UTILITIES
═══════════════════════════════════════════ */

/* Fluid container that collapses columns on small screens */
@media (max-width: 768px) {{
    /* Stack Streamlit columns vertically */
    [data-testid="column"] {{
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }}

    /* Shrink dashboard header text */
    .dash-header h1 {{
        font-size: 18px !important;
    }}
    .dash-header p {{
        font-size: 11px !important;
    }}
    .dash-header {{
        padding: 16px !important;
        gap: 12px !important;
        flex-wrap: wrap;
    }}
    .dash-header-icon {{
        font-size: 28px !important;
    }}
    /* Profile picture in header */
    .dash-header img, .dash-header > div:first-child {{
        width: 56px !important;
        height: 56px !important;
    }}

    /* KPI cards: make value smaller */
    .kpi-value {{
        font-size: 22px !important;
    }}
    .kpi-card {{
        padding: 14px 16px !important;
    }}

    /* Section titles */
    .section-title {{
        font-size: 11px !important;
    }}

    /* Tabs: allow horizontal scroll on mobile */
    [data-testid="stTabs"] > div > div {{
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }}
    [data-testid="stTabs"] > div > div > div > button {{
        font-size: 12px !important;
        padding: 6px 10px !important;
        white-space: nowrap;
    }}

    /* Record / product cards */
    .record-card {{
        padding: 12px !important;
    }}

    /* Price tag */
    .price-tag {{
        font-size: 15px !important;
    }}

    /* Buttons: full width on mobile */
    .stButton > button {{
        font-size: 12px !important;
        padding: 8px 10px !important;
    }}

    /* Forecast container */
    .forecast-container {{
        padding: 12px !important;
    }}

    /* Alert boxes */
    .alert-box {{
        font-size: 12px !important;
    }}

    /* Landing page hero */
    .hero-section h1 {{
        font-size: 24px !important;
    }}
    .hero-section p {{
        font-size: 13px !important;
    }}
    /* Stat cards grid → single column */
    .stats-grid {{
        grid-template-columns: 1fr !important;
    }}
}}

@media (min-width: 769px) and (max-width: 1024px) {{
    /* Tablet adjustments */
    .dash-header h1 {{
        font-size: 22px !important;
    }}
    .kpi-value {{
        font-size: 24px !important;
    }}
}}

@media (min-width: 1025px) {{
    /* Desktop — default sizes, nothing overridden */
}}

/* ═══════════════════════════════════════════
   MAIN CONTENT — always dark
═══════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"] {{
    background: #0f1117 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ═══════════════════════════════════════════
   SIDEBAR — togglable light / dark
═══════════════════════════════════════════ */
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
/* Sidebar pills */
[data-testid="stSidebar"] .pill {{
    background: {t["pill_bg"]} !important;
    color: {t["pill_color"]} !important;
    border-color: {t["pill_border"]} !important;
}}
/* Override specific colored pills to keep their semantic color in light mode */
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
/* Sidebar toggle label */
.sidebar-theme-toggle-label {{
    font-size: 12px;
    font-weight: 600;
    color: {t["sidebar_subtext"]};
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
    display: block;
}}
/* Toggle switch visual */
[data-testid="stSidebar"] [data-testid="stToggle"] {{
    accent-color: #16a34a;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  THEME TOGGLE WIDGET  (render inside st.sidebar block)
# ══════════════════════════════════════════════════════════════
def render_theme_toggle():
    """
    Call this inside `with st.sidebar:` on every page.
    Toggles ONLY the sidebar between light and dark.
    Main content is always dark — unaffected.

    Uses on_change callback so the toggle state is committed to
    session_state BEFORE Streamlit re-runs the page — this means
    it survives navigation between pages with no extra st.rerun().
    """
    # Initialise the session-state key if this is the first load
    if "sidebar_light_mode" not in st.session_state:
        st.session_state["sidebar_light_mode"] = False

    def _on_toggle_change():
        # Mirror widget value to our canonical session-state key
        st.session_state["sidebar_light_mode"] = st.session_state["_sb_toggle"]
        # inject_theme() re-runs at top of each page on the next Streamlit
        # re-run (triggered automatically by the toggle change), so the new
        # sidebar CSS is applied without an extra st.rerun() call.

    is_light = st.session_state["sidebar_light_mode"]
    label = "☀️ Light Sidebar" if not is_light else "🌙 Dark Sidebar"

    st.toggle(
        label,
        value=is_light,
        key="_sb_toggle",
        on_change=_on_toggle_change,
        help="Switch the sidebar between light and dark. Main content stays dark.",
    )


# ══════════════════════════════════════════════════════════════
#  PAGE HEADER HELPER  (optional convenience)
# ══════════════════════════════════════════════════════════════
def render_page_header(title: str, subtitle: str = "", icon: str = "🌾"):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        border-radius: 14px; padding: 28px 32px; margin-bottom: 24px; color: white;
    ">
        <div style="font-size: 36px; margin-bottom: 10px;">{icon}</div>
        <h2 style="margin: 0; font-size: clamp(18px, 3vw, 26px); font-weight: 700;">{title}</h2>
        { f'<p style="margin: 6px 0 0; opacity: 0.82; font-size: 14px;">{subtitle}</p>' if subtitle else '' }
    </div>
    """, unsafe_allow_html=True)
