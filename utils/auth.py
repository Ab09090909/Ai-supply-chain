"""Authentication helpers."""
import re as _re
import streamlit as st
from utils.db_helpers import get_supabase_client, cached_get_profile, clear_data_cache
from utils.constants import SESSION_KEYS

supabase = get_supabase_client()


def _sanitize_email(email: str) -> str:
    email = email.strip()
    email = _re.sub(r"^mailto:", "", email, flags=_re.IGNORECASE)
    email = _re.sub(r"[^ -~]", "", email)
    return email.strip()


def _valid_email(email: str) -> bool:
    return bool(_re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def sign_up(email, password, full_name, role, region, phone):
    email = _sanitize_email(email)
    if not _valid_email(email):
        return False, f"Invalid email: '{email}'."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    try:
        auth_res = supabase.auth.sign_up({"email": email, "password": password})
        if auth_res.user is None:
            return False, "Sign up failed. Email may already be registered."
        supabase.table("profiles").insert({
            "id": auth_res.user.id,
            "full_name": full_name,
            "role": role,
            "region": region,
            "phone": phone,
            "is_verified": False,
            "documents_uploaded": False,
        }).execute()
        return True, "Account created! Please log in."
    except Exception as e:
        return False, f"Sign up failed: {str(e)}"


def sign_in(email, password):
    email = _sanitize_email(email)
    try:
        auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if auth_res.user:
            st.session_state.user = auth_res.user
            st.session_state.profile = cached_get_profile(auth_res.user.id)
            return True, "Logged in successfully."
        return False, "Invalid credentials."
    except Exception as e:
        return False, f"Login failed: {e}"


def sign_out():
    supabase.auth.sign_out()
    for _k in SESSION_KEYS:
        if _k in st.session_state:
            del st.session_state[_k]
    if "theme_injected" in st.session_state:
        del st.session_state["theme_injected"]
    clear_data_cache()


def forgot_password(email: str):
    email = _sanitize_email(email)
    if not _valid_email(email):
        return False, f"Invalid email: '{email}'"
    try:
        supabase.auth.reset_password_email(email)
        return True, "Password reset email sent! Check your inbox."
    except Exception as e:
        return False, f"Reset failed: {e}"
