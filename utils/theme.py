# utils/theme.py
import streamlit as st

def initialize_theme():
    """Initialize theme state"""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'dark'  # Default to dark mode

def toggle_theme():
    """Toggle between dark and light mode"""
    current = st.session_state.theme_mode
    st.session_state.theme_mode = 'light' if current == 'dark' else 'dark'
    st.rerun()

def get_theme_css():
    """Get theme-specific CSS with proper contrast"""
    
    dark_css = """
    /* ===== DARK THEME ===== */
    /* Backgrounds */
    .stApp, .main > div {
        background: #0a0e1a;
    }
    
    /* Text Colors - High Contrast */
    .stMarkdown, .stText, .stCaption, .stMetric,
    .stMarkdown p, .stText p {
        color: #e2e8f0 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }
    
    /* Metric Cards */
    .stMetric label {
        color: #94a3b8 !important;
    }
    .stMetric .stMetricValue {
        color: #f8fafc !important;
    }
    
    /* Inputs */
    .stSelectbox, .stTextInput, .stNumberInput, .stTextArea {
        background: #1a1a2e;
    }
    .stSelectbox input, .stTextInput input, .stNumberInput input, 
    .stTextArea textarea, .stSelectbox div {
        background: #1a1a2e !important;
        color: #f8fafc !important;
        border-color: #2d3748 !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background: #1a1a2e !important;
    }
    .stSelectbox ul {
        background: #1a1a2e !important;
    }
    .stSelectbox li {
        color: #f8fafc !important;
    }
    .stSelectbox li:hover {
        background: #2d3748 !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        background: #1a1a2e;
        color: #f8fafc;
    }
    .stDataFrame thead tr th {
        background: #1a1a2e;
        color: #f8fafc;
    }
    .stDataFrame tbody tr td {
        background: #1a1a2e;
        color: #f8fafc;
    }
    
    /* Expanders */
    .stExpander {
        background: #1a1a2e;
        border-color: #2d3748;
    }
    .stExpander summary {
        color: #f8fafc !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1a2e;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #667eea !important;
    }
    
    /* Sidebar */
    .stSidebar {
        background: #0a0e1a;
    }
    .stSidebar .stMarkdown, .stSidebar .stText {
        color: #f8fafc !important;
    }
    .stSidebar .stMarkdown p {
        color: #f8fafc !important;
    }
    
    /* Alerts */
    .stAlert {
        background: #1a1a2e;
        border-color: #2d3748;
    }
    .stAlert .stMarkdown p {
        color: #f8fafc !important;
    }
    .stSuccess {
        background: rgba(16,185,129,0.15) !important;
        border-color: #10b981 !important;
    }
    .stWarning {
        background: rgba(245,158,11,0.15) !important;
        border-color: #f59e0b !important;
    }
    .stError {
        background: rgba(239,68,68,0.15) !important;
        border-color: #ef4444 !important;
    }
    .stInfo {
        background: rgba(59,130,246,0.15) !important;
        border-color: #3b82f6 !important;
    }
    .stAlert .stMarkdown p {
        color: #f8fafc !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Business Card */
    .business-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border-color: #2d3748 !important;
    }
    .business-card .card-name {
        color: #f8fafc !important;
    }
    .business-card .card-title {
        color: #94a3b8 !important;
    }
    .business-card .contact-item {
        color: #e2e8f0 !important;
    }
    .business-card .contact-label {
        color: #94a3b8 !important;
    }
    .business-card .contact-value {
        color: #f8fafc !important;
    }
    
    /* Metric Cards */
    .metric-card, .klip-card, .chart-card, .metric-sm {
        background: #1a1a2e !important;
        border-color: #2d3748 !important;
    }
    .metric-card .value, .klip-card .klip-value, .metric-sm .value {
        color: #f8fafc !important;
    }
    .metric-card .label, .klip-card .klip-title, .metric-sm .label {
        color: #94a3b8 !important;
    }
    .metric-card .sub, .klip-card .klip-sub, .metric-sm .sub {
        color: #64748b !important;
    }
    .metric-card .up, .klip-card .up { color: #10b981 !important; }
    .metric-card .down, .klip-card .down { color: #ef4444 !important; }
    
    /* Product Card */
    .product-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border-color: #2d3748 !important;
    }
    .product-card h4 {
        color: #f8fafc !important;
    }
    .product-card p {
        color: #94a3b8 !important;
    }
    .producer-info {
        background: rgba(102, 126, 234, 0.1) !important;
        color: #94a3b8 !important;
    }
    
    /* AI Insights */
    .ai-insight-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border-color: #2d3748 !important;
        color: #e2e8f0 !important;
    }
    .ai-insight-card strong {
        color: #f8fafc !important;
    }
    
    /* Dashboard */
    .dash-header {
        border-bottom-color: #2d3748 !important;
    }
    .dash-header h1 {
        color: #f8fafc !important;
    }
    .row-sm {
        border-bottom-color: #1e293b !important;
    }
    .row-sm .name {
        color: #e2e8f0 !important;
    }
    .row-sm .meta {
        color: #94a3b8 !important;
    }
    .row-sm .val {
        color: #10b981 !important;
    }
    
    /* Checkboxes and Radio */
    .stCheckbox label {
        color: #e2e8f0 !important;
    }
    .stRadio label {
        color: #e2e8f0 !important;
    }
    
    /* File Uploader */
    .stFileUploader div {
        background: #1a1a2e;
        border-color: #2d3748;
        color: #e2e8f0;
    }
    .stFileUploader div:hover {
        border-color: #667eea;
    }
    
    /* Progress Bar */
    .stProgress .stProgressBar {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* Section Titles */
    .section-title {
        color: #94a3b8 !important;
    }
    """
    
    light_css = """
    /* ===== LIGHT THEME ===== */
    /* Backgrounds */
    .stApp, .main > div {
        background: #f1f5f9;
    }
    
    /* Text Colors - High Contrast */
    .stMarkdown, .stText, .stCaption, .stMetric,
    .stMarkdown p, .stText p {
        color: #1e293b !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
    }
    
    /* Metric Labels */
    .stMetric label {
        color: #475569 !important;
    }
    .stMetric .stMetricValue {
        color: #0f172a !important;
    }
    
    /* Inputs - Light background with dark text */
    .stSelectbox, .stTextInput, .stNumberInput, .stTextArea {
        background: #ffffff !important;
    }
    .stSelectbox input, .stTextInput input, .stNumberInput input, 
    .stTextArea textarea, .stSelectbox div {
        background: #ffffff !important;
        color: #1e293b !important;
        border-color: #cbd5e1 !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background: #ffffff !important;
        color: #1e293b !important;
    }
    .stSelectbox ul {
        background: #ffffff !important;
    }
    .stSelectbox li {
        color: #1e293b !important;
    }
    .stSelectbox li:hover {
        background: #f1f5f9 !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        background: #ffffff;
        color: #1e293b;
    }
    .stDataFrame thead tr th {
        background: #f1f5f9;
        color: #1e293b;
    }
    .stDataFrame tbody tr td {
        background: #ffffff;
        color: #1e293b;
    }
    
    /* Expanders */
    .stExpander {
        background: #ffffff;
        border-color: #e2e8f0;
    }
    .stExpander summary {
        color: #1e293b !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff;
    }
    .stTabs [data-baseweb="tab"] {
        color: #475569 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #667eea !important;
    }
    
    /* Sidebar */
    .stSidebar {
        background: #f8fafc;
    }
    .stSidebar .stMarkdown, .stSidebar .stText {
        color: #1e293b !important;
    }
    .stSidebar .stMarkdown p {
        color: #1e293b !important;
    }
    
    /* Alerts */
    .stAlert {
        background: #ffffff;
        border-color: #e2e8f0;
    }
    .stAlert .stMarkdown p {
        color: #1e293b !important;
    }
    .stSuccess {
        background: rgba(16,185,129,0.1) !important;
        border-color: #10b981 !important;
    }
    .stWarning {
        background: rgba(245,158,11,0.1) !important;
        border-color: #f59e0b !important;
    }
    .stError {
        background: rgba(239,68,68,0.1) !important;
        border-color: #ef4444 !important;
    }
    .stInfo {
        background: rgba(59,130,246,0.1) !important;
        border-color: #3b82f6 !important;
    }
    .stAlert .stMarkdown p {
        color: #1e293b !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Business Card */
    .business-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: #e2e8f0 !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1) !important;
    }
    .business-card .card-name {
        color: #0f172a !important;
    }
    .business-card .card-title {
        color: #475569 !important;
    }
    .business-card .contact-item {
        color: #1e293b !important;
    }
    .business-card .contact-label {
        color: #475569 !important;
    }
    .business-card .contact-value {
        color: #0f172a !important;
    }
    
    /* Metric Cards */
    .metric-card, .klip-card, .chart-card, .metric-sm {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    .metric-card .value, .klip-card .klip-value, .metric-sm .value {
        color: #0f172a !important;
    }
    .metric-card .label, .klip-card .klip-title, .metric-sm .label {
        color: #475569 !important;
    }
    .metric-card .sub, .klip-card .klip-sub, .metric-sm .sub {
        color: #64748b !important;
    }
    .metric-card .up, .klip-card .up { color: #10b981 !important; }
    .metric-card .down, .klip-card .down { color: #ef4444 !important; }
    
    /* Product Card */
    .product-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: #e2e8f0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    .product-card h4 {
        color: #0f172a !important;
    }
    .product-card p {
        color: #475569 !important;
    }
    .producer-info {
        background: rgba(102, 126, 234, 0.05) !important;
        color: #475569 !important;
    }
    .product-info-badge {
        background: #e2e8f0 !important;
        color: #475569 !important;
    }
    
    /* AI Insights */
    .ai-insight-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: #e2e8f0 !important;
        color: #1e293b !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    .ai-insight-card strong {
        color: #0f172a !important;
    }
    
    /* Dashboard */
    .dash-header {
        border-bottom-color: #e2e8f0 !important;
    }
    .dash-header h1 {
        color: #0f172a !important;
    }
    .row-sm {
        border-bottom-color: #e2e8f0 !important;
    }
    .row-sm .name {
        color: #1e293b !important;
    }
    .row-sm .meta {
        color: #64748b !important;
    }
    .row-sm .val {
        color: #10b981 !important;
    }
    
    /* Badges */
    .badge-sm.delivered { background: rgba(16,185,129,0.15); color: #10b981; }
    .badge-sm.pending { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .badge-sm.shipped { background: rgba(59,130,246,0.15); color: #3b82f6; }
    .badge-sm.cancelled { background: rgba(239,68,68,0.15); color: #ef4444; }
    
    /* Checkboxes and Radio */
    .stCheckbox label {
        color: #1e293b !important;
    }
    .stRadio label {
        color: #1e293b !important;
    }
    
    /* File Uploader */
    .stFileUploader div {
        background: #ffffff;
        border-color: #e2e8f0;
        color: #1e293b;
    }
    .stFileUploader div:hover {
        border-color: #667eea;
    }
    
    /* Progress Bar */
    .stProgress .stProgressBar {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* Section Titles */
    .section-title {
        color: #475569 !important;
    }
    
    /* Captions and small text */
    .stCaption, .stCaption p {
        color: #64748b !important;
    }
    
    /* Info messages */
    .stInfo .stMarkdown p {
        color: #1e293b !important;
    }
    .stWarning .stMarkdown p {
        color: #1e293b !important;
    }
    .stSuccess .stMarkdown p {
        color: #1e293b !important;
    }
    .stError .stMarkdown p {
        color: #1e293b !important;
    }
    
    /* Metric delta colors */
    .stMetric .stMetricDelta {
        color: #10b981 !important;
    }
    .stMetric .stMetricDeltaNegative {
        color: #ef4444 !important;
    }
    """
    
    if st.session_state.theme_mode == 'dark':
        return dark_css
    else:
        return light_css

def render_theme_toggle():
    """Render theme toggle button in sidebar"""
    st.sidebar.markdown("---")
    
    if st.session_state.theme_mode == 'dark':
        icon = "☀️"
        label = "Light Mode"
    else:
        icon = "🌙"
        label = "Dark Mode"
    
    if st.sidebar.button(f"{icon} {label}", use_container_width=True):
        toggle_theme()
