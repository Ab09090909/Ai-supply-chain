"""Authentication utilities for Supabase."""
import streamlit as st
from utils.db_helpers import supabase, clear_data_cache

def sign_up(email, password, full_name, role, region, phone=""):
    """Register a new user."""
    try:
        # Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        
        if response.user:
            user_id = response.user.id
            
            # Create profile
            profile_data = {
                "id": user_id,
                "full_name": full_name,
                "role": role,
                "region": region,
                "phone": phone or None,
                "is_verified": False,
                "documents_uploaded": False,
            }
            supabase.table("profiles").insert(profile_data).execute()
            
            return True, "Account created successfully! Please check your email to verify."
        else:
            return False, "Signup failed. Please try again."
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return False, "This email is already registered. Please sign in."
        return False, f"Signup error: {error_msg}"

def sign_in(email, password):
    """Sign in an existing user."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        
        if response.user:
            st.session_state.user = response.user
            clear_data_cache()
            
            # Load profile
            profile = supabase.table("profiles").select("*").eq("id", response.user.id).execute()
            if profile.data:
                st.session_state.profile = profile.data[0]
            
            return True, "Signed in successfully!"
        else:
            return False, "Invalid email or password."
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return False, "Invalid email or password. Please try again."
        return False, f"Login error: {error_msg}"

def sign_out():
    """Sign out the current user."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    
    # Clear session state
    st.session_state.user = None
    st.session_state.profile = None
    st.session_state.auth_redirect = False
    clear_data_cache()

def forgot_password(email):
    """Send password reset email."""
    try:
        supabase.auth.reset_password_for_email(email)
        return True, "Password reset link sent to your email."
    except Exception as e:
        return False, f"Password reset failed: {str(e)}"

def get_current_user():
    """Get the current authenticated user."""
    if st.session_state.get("user"):
        return st.session_state.user
    
    try:
        session = supabase.auth.get_session()
        if session:
            st.session_state.user = session.user
            return session.user
    except Exception:
        pass
    
    return None
