# pages/producer/main.py
import streamlit as st

# --- Imports from utils ---
from utils.auth import initialize_session_state
from utils.db_helpers import get_products

# --- Import local modules ---
from .components.profile import render_profile, render_edit_profile
from .tabs.dashboard import render_dashboard
from .tabs.inventory import render_inventory
from .tabs.orders import render_orders
from .tabs.ai_insights import render_ai_insights
from .utils.self_learning_ai import SelfLearningAI

def render_producer_page():
    """Main entry point for producer page"""
    
    # Initialize session state
    initialize_session_state()
    
    # --- Authentication Guard ---
    if not st.session_state.authenticated:
        st.error("🔒 Please log in to access this page.")
        st.stop()
    
    if st.session_state.user_info['role'] != 'producer':
        st.error("⛔ Access Denied. This page is for Producers only.")
        st.stop()
    
    user_info = st.session_state.user_info
    
    # --- Initialize ALL States ---
    if 'show_edit_profile' not in st.session_state:
        st.session_state.show_edit_profile = False
    
    if 'edit_product_id' not in st.session_state:
        st.session_state.edit_product_id = None
    
    if 'delete_product_id' not in st.session_state:
        st.session_state.delete_product_id = None
    
    if 'ai_selected_product' not in st.session_state:
        st.session_state.ai_selected_product = None
    
    if 'ai_selected_region' not in st.session_state:
        st.session_state.ai_selected_region = 'Addis Ababa'
    
    if 'inventory_subtab' not in st.session_state:
        st.session_state.inventory_subtab = "My Products"
    
    # Initialize AI
    ai = SelfLearningAI(user_info['id'])
    
    # Render profile
    render_profile(user_info)
    
    # Render edit profile
    render_edit_profile(user_info)
    
    st.markdown("---")
    
    # --- Navigation Tabs ---
    tab_dashboard, tab_inventory, tab_orders, tab_ai = st.tabs([
        "📊 Dashboard", "📦 Inventory", "🚚 Orders", "🤖 AI Insights"
    ])
    
    # Render each tab
    with tab_dashboard:
        render_dashboard(user_info, ai)
    
    with tab_inventory:
        render_inventory(user_info, ai)
    
    with tab_orders:
        render_orders(user_info)
    
    with tab_ai:
        render_ai_insights(user_info, ai)

# For backward compatibility with existing page routing
if __name__ == "__main__":
    render_producer_page()
