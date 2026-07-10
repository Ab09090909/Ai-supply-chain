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
    """Get theme-specific CSS"""
    
    dark_css = """
    /* Dark Theme */
    .stApp {
        background: #0a0e1a;
    }
    .main > div {
        background: #0a0e1a;
    }
    .stMarkdown, .stText, .stCaption, .stMetric {
        color: #f8fafc;
    }
    .stMetric label {
        color: #94a3b8 !important;
    }
    .stMetric .stMetricValue {
        color: #f8fafc !important;
    }
    .stSelectbox, .stTextInput, .stNumberInput, .stTextArea {
        background: #1a1a2e;
        color: #f8fafc;
    }
    .stSelectbox input, .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: #1a1a2e;
        color: #f8fafc;
        border-color: #2d3748;
    }
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
    .stExpander {
        background: #1a1a2e;
        border-color: #2d3748;
    }
    .stExpander summary {
        color: #f8fafc;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1a2e;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #667eea;
    }
    .stSidebar {
        background: #0a0e1a;
    }
    .stSidebar .stMarkdown, .stSidebar .stText {
        color: #f8fafc;
    }
    .stAlert {
        background: #1a1a2e;
        border-color: #2d3748;
    }
    .stSuccess {
        background: rgba(16,185,129,0.1);
        border-color: #10b981;
    }
    .stWarning {
        background: rgba(245,158,11,0.1);
        border-color: #f59e0b;
    }
    .stError {
        background: rgba(239,68,68,0.1);
        border-color: #ef4444;
    }
    .stInfo {
        background: rgba(59,130,246,0.1);
        border-color: #3b82f6;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
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
    .ai-insight-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border-color: #2d3748 !important;
        color: #e2e8f0 !important;
    }
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
    .stSelectbox div[data-baseweb="select"] {
        background: #1a1a2e;
        color: #f8fafc;
    }
    .stSelectbox ul {
        background: #1a1a2e;
    }
    .stSelectbox li {
        color: #f8fafc;
    }
    .stSelectbox li:hover {
        background: #2d3748;
    }
    .stDateInput input {
        background: #1a1a2e;
        color: #f8fafc;
    }
    .stSlider .stSliderTrack {
        background: #2d3748;
    }
    .stSlider .stSliderThumb {
        background: #667eea;
    }
    .stCheckbox label {
        color: #f8fafc;
    }
    .stRadio label {
        color: #f8fafc;
    }
    .stMultiselect div {
        background: #1a1a2e;
        color: #f8fafc;
    }
    .stFileUploader div {
        background: #1a1a2e;
        border-color: #2d3748;
        color: #f8fafc;
    }
    .stFileUploader div:hover {
        border-color: #667eea;
    }
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    .stProgress .stProgressBar {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    """
    
    light_css = """
    /* Light Theme */
    .stApp {
        background: #f8fafc;
    }
    .main > div {
        background: #f8fafc;
    }
    .stMarkdown, .stText, .stCaption, .stMetric {
        color: #1e293b;
    }
    .stMetric label {
        color: #64748b !important;
    }
    .stMetric .stMetricValue {
        color: #1e293b !important;
    }
    .stSelectbox, .stTextInput, .stNumberInput, .stTextArea {
        background: #ffffff;
        color: #1e293b;
    }
    .stSelectbox input, .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: #ffffff;
        color: #1e293b;
        border-color: #e2e8f0;
    }
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
    .stExpander {
        background: #ffffff;
        border-color: #e2e8f0;
    }
    .stExpander summary {
        color: #1e293b;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748b;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #667eea;
    }
    .stSidebar {
        background: #f8fafc;
    }
    .stSidebar .stMarkdown, .stSidebar .stText {
        color: #1e293b;
    }
    .stAlert {
        background: #ffffff;
        border-color: #e2e8f0;
    }
    .stSuccess {
        background: rgba(16,185,129,0.1);
        border-color: #10b981;
    }
    .stWarning {
        background: rgba(245,158,11,0.1);
        border-color: #f59e0b;
    }
    .stError {
        background: rgba(239,68,68,0.1);
        border-color: #ef4444;
    }
    .stInfo {
        background: rgba(59,130,246,0.1);
        border-color: #3b82f6;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .business-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: #e2e8f0 !important;
    }
    .business-card .card-name {
        color: #1e293b !important;
    }
    .business-card .card-title {
        color: #64748b !important;
    }
    .business-card .contact-item {
        color: #1e293b !important;
    }
    .business-card .contact-label {
        color: #475569 !important;
    }
    .business-card .contact-value {
        color: #1e293b !important;
    }
    .metric-card, .klip-card, .chart-card, .metric-sm {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
    }
    .metric-card .value, .klip-card .klip-value, .metric-sm .value {
        color: #1e293b !important;
    }
    .metric-card .label, .klip-card .klip-title, .metric-sm .label {
        color: #64748b !important;
    }
    .product-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: #e2e8f0 !important;
    }
    .product-card h4 {
        color: #1e293b !important;
    }
    .product-card p {
        color: #64748b !important;
    }
    .producer-info {
        background: rgba(102, 126, 234, 0.05) !important;
        color: #475569 !important;
    }
    .ai-insight-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border-color: #e2e8f0 !important;
        color: #1e293b !important;
    }
    .dash-header {
        border-bottom-color: #e2e8f0 !important;
    }
    .dash-header h1 {
        color: #1e293b !important;
    }
    .row-sm {
        border-bottom-color: #e2e8f0 !important;
    }
    .row-sm .name {
        color: #1e293b !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background: #ffffff;
        color: #1e293b;
    }
    .stSelectbox ul {
        background: #ffffff;
    }
    .stSelectbox li {
        color: #1e293b;
    }
    .stSelectbox li:hover {
        background: #f1f5f9;
    }
    .stDateInput input {
        background: #ffffff;
        color: #1e293b;
    }
    .stSlider .stSliderTrack {
        background: #e2e8f0;
    }
    .stSlider .stSliderThumb {
        background: #667eea;
    }
    .stCheckbox label {
        color: #1e293b;
    }
    .stRadio label {
        color: #1e293b;
    }
    .stMultiselect div {
        background: #ffffff;
        color: #1e293b;
    }
    .stFileUploader div {
        background: #ffffff;
        border-color: #e2e8f0;
        color: #1e293b;
    }
    .stFileUploader div:hover {
        border-color: #667eea;
    }
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    .stProgress .stProgressBar {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
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
