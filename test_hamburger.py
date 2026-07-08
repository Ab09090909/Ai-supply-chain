"""
test_hamburger.py — Test page for hamburger menu
"""
import streamlit as st

st.set_page_config(
    page_title="Test Hamburger",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── SESSION STATE ───
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# ─── CSS ───
st.markdown("""
<style>
/* Hide default sidebar */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}
#MainMenu, footer, header {
    visibility: hidden !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}

/* Hamburger button */
.hamburger-btn {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 999997;
    background: #1B4332;
    color: white;
    border: 2px solid #2D6A4F;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 24px;
    cursor: pointer;
}

/* Sidebar overlay */
.mobile-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    z-index: 999998;
}
.mobile-overlay.active {
    display: block;
}

/* Custom sidebar */
.mobile-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 280px;
    height: 100%;
    background: #161b27;
    z-index: 999999;
    padding: 20px;
    border-right: 1px solid #1e2a3a;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
}
.mobile-sidebar.open {
    transform: translateX(0);
}

.close-btn {
    background: transparent;
    border: none;
    color: #e2e8f0;
    font-size: 24px;
    cursor: pointer;
    float: right;
}
.close-btn:hover {
    color: #f87171;
}

.sidebar-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #1e2a3a;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    font-size: 24px;
    color: #f1f5f9;
    font-weight: 700;
    border: 2px solid #D4A017;
}
.sidebar-name {
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    color: #e2e8f0;
    margin-top: 10px;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid #1e2a3a;
    margin: 15px 0;
}
.sidebar-btn {
    width: 100%;
    padding: 10px 14px;
    margin-bottom: 4px;
    background: #1e2a3a;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 14px;
    cursor: pointer;
    text-align: left;
}
.sidebar-btn:hover {
    border-color: #D4A017;
    color: #D4A017;
}

/* Main content */
[data-testid="stAppViewBlockContainer"] {
    padding-top: 70px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── HAMBURGER MENU ───
def render_hamburger():
    """Render hamburger menu."""
    
    # Get menu state
    is_open = st.session_state.get("menu_open", False)
    open_class = "open" if is_open else ""
    overlay_class = "active" if is_open else ""
    
    # HTML
    st.markdown(f'''
    <!-- Hamburger Button -->
    <button class="hamburger-btn" onclick="
        var sidebar = document.getElementById('testSidebar');
        var overlay = document.getElementById('testOverlay');
        if (sidebar.classList.contains('open')) {{
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        }} else {{
            sidebar.classList.add('open');
            overlay.classList.add('active');
        }}
    ">☰</button>
    
    <!-- Overlay -->
    <div class="mobile-overlay {overlay_class}" id="testOverlay" onclick="
        document.getElementById('testSidebar').classList.remove('open');
        this.classList.remove('active');
    "></div>
    
    <!-- Sidebar -->
    <div class="mobile-sidebar {open_class}" id="testSidebar">
        <button class="close-btn" onclick="
            document.getElementById('testSidebar').classList.remove('open');
            document.getElementById('testOverlay').classList.remove('active');
        ">✕</button>
        
        <div style="text-align: center; margin-top: 10px;">
            <div class="sidebar-avatar">🧪</div>
            <div class="sidebar-name">Test User</div>
        </div>
        
        <hr class="sidebar-divider">
        
        <button class="sidebar-btn" onclick="window.location.href='app.py'">🏠 Home</button>
        <button class="sidebar-btn" onclick="window.location.href='pages/1_producer.py'">🚜 Producer</button>
        <button class="sidebar-btn" onclick="window.location.href='test_hamburger.py'">🧪 Test</button>
        
        <hr class="sidebar-divider">
        
        <button class="sidebar-btn" style="color: #f87171; border-color: #ef444455;" onclick="alert('Logout clicked!')">🚪 Log Out</button>
    </div>
    ''', unsafe_allow_html=True)

# ─── MAIN CONTENT ───
def main():
    """Main function."""
    
    render_hamburger()
    
    st.title("🧪 Hamburger Menu Test")
    st.markdown("---")
    
    st.markdown("""
    ### ✅ This is a test page
    
    **Instructions:**
    1. Click the **☰** button in the top-left corner
    2. The sidebar should slide in from the left
    3. Click **✕** or the overlay to close it
    4. Click **Test** button to stay on this page
    
    ### Session State:
    """)
    
    st.write(f"`menu_open` = {st.session_state.get('menu_open', False)}")
    
    if st.button("🔄 Toggle Menu (Streamlit)"):
        st.session_state.menu_open = not st.session_state.menu_open
        st.rerun()
    
    st.markdown("---")
    st.caption("If the hamburger menu works here, the issue is in the producer page.")

if __name__ == "__main__":
    main()
