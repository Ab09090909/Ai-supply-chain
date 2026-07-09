import streamlit as st
from utils.db_helpers import update_user

def render_profile(user_info):
    """Render producer profile card"""
    name = user_info.get('name', 'Not specified')
    initial = name[0].upper() if name else "P"
    
    # Simple profile display
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    width: 80px; height: 80px; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 32px; font-weight: bold; color: white;">
            {initial}
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"### {name}")
        st.caption(f"Role: Producer | Region: {user_info.get('region', 'N/A')}")
        st.caption(f"Email: {user_info.get('email', 'N/A')}")
