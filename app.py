import streamlit as st
from utils.auth import initialize_session_state, login_user, register_user, logout_user
from utils.shared_ui import render_custom_css, render_sidebar

st.set_page_config(page_title="AI Supply Chain", page_icon="🚀", layout="wide")
initialize_session_state()
render_custom_css()

if not st.session_state.authenticated:
    st.title("🚀 AI Supply Chain Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                success, msg, user = login_user(email, password)
                if success: st.success(msg)
                else: st.error(msg)
    
    with tab2:
        with st.form("signup_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["producer", "merchant", "customer", "admin"])
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                success, msg = register_user(name, email, password, role)
                if success: st.success(msg)
                else: st.error(msg)
else:
    st.title(f"Welcome, {st.session_state.user_info['name']}!")
    if st.button("Logout"):
        logout_user()
