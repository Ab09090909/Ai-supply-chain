import streamlit as st
from utils.db_helpers import update_user, get_user_by_id


def render_profile(user_info):
    """Render producer profile header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"🌾 Welcome, {user_info.get('name', 'Producer')}!")
        st.caption(f"📧 {user_info.get('email', '')} | 📍 {user_info.get('location', 'Ethiopia')}")
    with col2:
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.show_edit_profile = not st.session_state.get('show_edit_profile', False)


def render_edit_profile(user_info):
    """Render edit profile form"""
    if not st.session_state.get('show_edit_profile', False):
        return

    with st.expander("✏️ Edit Profile", expanded=True):
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", value=user_info.get('name', ''))
                phone = st.text_input("Phone", value=user_info.get('phone', ''))
            with col2:
                location = st.text_input("Location", value=user_info.get('location', ''))
                farm_size = st.text_input("Farm Size (hectares)", value=str(user_info.get('farm_size', '')))

            bio = st.text_area("Bio / Description", value=user_info.get('bio', ''), height=80)

            col_save, col_cancel = st.columns(2)
            with col_save:
                submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

            if submitted:
                success, msg = update_user(
                    user_info['id'],
                    name=name,
                    phone=phone,
                    location=location,
                    farm_size=farm_size,
                    bio=bio
                )
                if success:
                    st.success("✅ Profile updated!")
                    updated = get_user_by_id(user_info['id'])
                    if updated:
                        st.session_state.user_info = updated
                    st.session_state.show_edit_profile = False
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

            if cancelled:
                st.session_state.show_edit_profile = False
                st.rerun()
