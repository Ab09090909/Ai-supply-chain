import streamlit as st
from utils.auth import initialize_session_state
from utils.db_helpers import get_products
from pages.producer.components.profile import render_profile, render_edit_profile
from pages.producer.tabs.dashboard import render_dashboard
from pages.producer.tabs.inventory import render_inventory
from pages.producer.tabs.orders import render_orders
from pages.producer.tabs.ai_insights import render_ai_insights
from pages.producer.utils.self_learning_ai import SelfLearningAI

def render_producer_page():
    initialize_session_state()

    if not st.session_state.authenticated:
        st.error("🔒 Please log in.")
        st.stop()

    if st.session_state.user_info.get('role') != 'producer':
        st.error("⛔ Access Denied.")
        st.stop()

    user_info = st.session_state.user_info

    if 'show_edit_profile' not in st.session_state:
        st.session_state.show_edit_profile = False

    ai = SelfLearningAI(user_info['id'])

    render_profile(user_info)
    render_edit_profile(user_info)
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📦 Inventory", "🚚 Orders", "🤖 AI Insights"])

    with tab1:
        render_dashboard(user_info, ai)
    with tab2:
        render_inventory(user_info, ai)
    with tab3:
        render_orders(user_info)
    with tab4:
        render_ai_insights(user_info, ai)
