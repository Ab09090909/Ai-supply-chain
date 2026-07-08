"""Authentication helpers."""
import re as _re
import streamlit as st
from utils.db_helpers import supabase, cached_get_profile
from utils.constants import SESSION_KEYS


def sign_in(email, password):
    """Sign in with email and password."""
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        st.session_state.profile = cached_get_profile(res.user.id)
        return True, "Signed in successfully!"
    except Exception as e:
        return False, f"Sign in failed: {str(e)}"


def sign_up(email, password, full_name, role, region, phone=None):
    """Sign up with email and password."""
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name, "role": role, "region": region, "phone": phone}}
        })
        if res.user:
            # Create profile in database
            supabase.table("profiles").insert({
                "id": res.user.id,
                "full_name": full_name,
                "role": role,
                "region": region,
                "phone": phone,
                "is_verified": False,
                "documents_uploaded": False
            }).execute()
            return True, "Account created successfully! Please sign in."
        return False, "Sign up failed."
    except Exception as e:
        return False, f"Sign up failed: {str(e)}"


def sign_out():
    """Sign out the current user."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    for key in SESSION_KEYS:
        if key in st.session_state:
            del st.session_state[key]


def forgot_password(email):
    """Send password reset email."""
    try:
        supabase.auth.reset_password_for_email(email)
        return True, "Password reset email sent! Check your inbox."
    except Exception as e:
        return False, f"Failed to send reset email: {str(e)}"
