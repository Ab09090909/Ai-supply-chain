def get_custom_css():
    """Return enhanced custom CSS"""
    return """
    <style>
    /* Global Styles */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Login Page Styles */
    .login-header {
        text-align: center;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .login-header p {
        color: #94a3b8;
        font-size: 1.1rem;
    }
    
    .login-features {
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 1rem;
        margin-top: 2rem;
    }
    
    .login-features h2 {
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .feature {
        display: flex;
        align-items: center;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
        transition: transform 0.3s ease;
    }
    
    .feature:hover {
        transform: translateX(10px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-right: 1.5rem;
    }
    
    .feature-text h3 {
        margin-bottom: 0.5rem;
        color: #e2e8f0;
    }
    
    .feature-text p {
        color: #94a3b8;
        margin: 0;
    }
    
    /* User Profile in Sidebar */
    .user-profile {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .user-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .user-info {
        flex: 1;
    }
    
    .user-name {
        font-weight: 600;
        font-size: 1rem;
        color: #e2e8f0;
    }
    
    .user-role {
        font-size: 0.875rem;
        color: #94a3b8;
        text-transform: capitalize;
    }
    
    /* Page Header */
    .page-header {
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
    }
    
    .page-title {
        font-size: 2rem;
        margin: 0;
        color: #e2e8f0;
    }
    
    .page-subtitle {
        color: #94a3b8;
        margin: 0.5rem 0 0 0;
    }
    
    /* Welcome Banner */
    .welcome-banner {
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        border-left: 4px solid;
    }
    
    .welcome-banner h1 {
        margin: 0 0 0.5rem 0;
        font-size: 2rem;
    }
    
    .welcome-banner p {
        margin: 0;
        opacity: 0.9;
    }
    
    /* Info Cards */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    
    .card-title {
        margin: 0;
        font-size: 1.25rem;
        color: #e2e8f0;
    }
    
    .card-content {
        color: #94a3b8;
        line-height: 1.6;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .metric-delta.green {
        color: #10b981;
    }
    
    .metric-delta.red {
        color: #ef4444;
    }
    
    /* Form Styles */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #e2e8f0;
        border-radius: 0.5rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Button Styles */
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1e293b;
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .login-header h1 {
            font-size: 2rem;
        }
        
        .welcome-banner h1 {
            font-size: 1.5rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
    </style>
    """

def get_role_colors(role: str) -> dict:
    """Get color scheme based on user role"""
    colors = {
        'producer': {
            'primary': '#10b981',
            'secondary': '#059669',
            'accent': '#34d399'
        },
        'merchant': {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#818cf8'
        },
        'customer': {
            'primary': '#f59e0b',
            'secondary': '#d97706',
            'accent': '#fbbf24'
        },
        'admin': {
            'primary': '#ef4444',
            'secondary': '#dc2626',
            'accent': '#f87171'
        }
    }
    
    return colors.get(role, colors['merchant'])
