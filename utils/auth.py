"""Authentication utilities for Supabase."""
import streamlit as st
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# LAZY IMPORT — avoids circular imports
# ─────────────────────────────────────────────────────────────
def get_supabase():
    """Lazy-load Supabase client to avoid circular imports."""
    from utils.db_helpers import supabase, clear_data_cache
    return supabase, clear_data_cache

# ─────────────────────────────────────────────────────────────
# SIGN UP
# ─────────────────────────────────────────────────────────────
def sign_up(
    email: str,
    password: str,
    full_name: str,
    role: str,
    region: str,
    phone: str = "",
) -> Tuple[bool, str]:
    """
    Register a new user and create their profile row.

    Returns:
        (success, message)
    """
    # Input validation
    if not email or "@" not in email:
        return False, "Please enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not full_name or len(full_name.strip()) < 2:
        return False, "Please enter your full name."

    try:
        supabase, _ = get_supabase()

        # Create auth user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": role,
                    "region": region,
                }
            },
        })

        if not (response and response.user):
            logger.warning(f"Signup failed for {email}: no user returned")
            return False, "Signup failed. Please try again."

        user_id = response.user.id

        # Create profile row — omit timestamps, let Supabase defaults handle them
        profile_data = {
            "id": user_id,
            "full_name": full_name.strip(),
            "role": role.lower(),
            "region": region,
            "phone": phone.strip() if phone else None,
            "is_verified": False,
            "documents_uploaded": False,
        }

        try:
            supabase.table("profiles").insert(profile_data).execute()
            logger.info(f"User registered: {email} / role: {role}")
            return True, "Account created! Please check your email to verify your account before signing in."
        except Exception as e:
            logger.error(f"Profile creation failed for {email}: {e}")
            # Note: admin.delete_user requires service-role key, not anon key.
            # The orphaned auth user will need manual cleanup in the Supabase dashboard.
            return False, f"Account created but profile setup failed: {str(e)}"

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Signup error for {email}: {error_msg}")

        if "already registered" in error_msg.lower():
            return False, "This email is already registered. Please sign in."
        if "password" in error_msg.lower():
            return False, "Password does not meet requirements. Use at least 8 characters."
        return False, f"Registration error: {error_msg}"

# ─────────────────────────────────────────────────────────────
# SIGN IN
# ─────────────────────────────────────────────────────────────
def sign_in(email: str, password: str) -> Tuple[bool, str]:
    """
    Sign in an existing user and populate session state.

    Returns:
        (success, message)
    """
    if not email or not password:
        return False, "Please enter both email and password."

    try:
        supabase, clear_data_cache = get_supabase()

        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if not (response and response.user):
            return False, "Invalid email or password. Please try again."

        # Populate session
        st.session_state.user = response.user
        st.session_state.authenticated = True
        st.session_state.user_email = response.user.email
        clear_data_cache()

        # Load profile
        try:
            profile_resp = (
                supabase.table("profiles")
                .select("*")
                .eq("id", response.user.id)
                .execute()
            )
            if profile_resp and profile_resp.data:
                st.session_state.profile = profile_resp.data[0]
                st.session_state.user_role = profile_resp.data[0].get("role", "customer")
                logger.info(f"Signed in: {email} as {st.session_state.user_role}")
            else:
                # Profile missing — create a default one
                logger.warning(f"No profile found for {email}, creating default")
                default_name = email.split("@")[0]
                profile_data = {
                    "id": response.user.id,
                    "full_name": default_name,
                    "role": "customer",
                    "region": "Addis Ababa",
                    "is_verified": False,
                    "documents_uploaded": False,
                }
                supabase.table("profiles").insert(profile_data).execute()
                profile_resp = (
                    supabase.table("profiles")
                    .select("*")
                    .eq("id", response.user.id)
                    .execute()
                )
                if profile_resp and profile_resp.data:
                    st.session_state.profile = profile_resp.data[0]
                    st.session_state.user_role = "customer"
        except Exception as e:
            logger.error(f"Profile load error for {email}: {e}")
            # Non-fatal — profile will be fetched on next render

        return True, "Signed in successfully!"

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Login error for {email}: {error_msg}")

        if "Invalid login credentials" in error_msg:
            return False, "Invalid email or password. Please try again."
        if "email not confirmed" in error_msg.lower():
            return False, "Please verify your email before signing in. Check your inbox."
        return False, f"Login error: {error_msg}"

# ─────────────────────────────────────────────────────────────
# SIGN OUT
# ─────────────────────────────────────────────────────────────
def sign_out() -> None:
    """Sign out the current user and clear all session state."""
    try:
        supabase, clear_data_cache = get_supabase()
        supabase.auth.sign_out()
        clear_data_cache()
    except Exception as e:
        logger.error(f"Sign out error: {e}")

    # Remove keys cleanly rather than setting to None
    for key in ["user", "profile", "authenticated", "user_role", "user_email",
                "auth_redirect", "nav_clicked", "menu_open"]:
        st.session_state.pop(key, None)

    logger.info("User signed out")

# ─────────────────────────────────────────────────────────────
# FORGOT PASSWORD
# ─────────────────────────────────────────────────────────────
def forgot_password(email: str) -> Tuple[bool, str]:
    """
    Send a password reset email via Supabase Auth.

    Returns:
        (success, message)
    """
    if not email or "@" not in email:
        return False, "Please enter a valid email address."

    try:
        supabase, _ = get_supabase()
        supabase.auth.reset_password_for_email(email)
        logger.info(f"Password reset email sent to: {email}")
        return True, "Password reset link sent! Check your inbox (and spam folder)."
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Password reset error for {email}: {error_msg}")
        if "not found" in error_msg.lower():
            return False, "No account found with this email address."
        return False, f"Failed to send reset email: {error_msg}"

# ─────────────────────────────────────────────────────────────
# SESSION HELPERS
# ─────────────────────────────────────────────────────────────
def get_current_user() -> Optional[Any]:
    """Return the current user from session state, refreshing from Supabase if needed."""
    if st.session_state.get("user"):
        return st.session_state.user

    try:
        supabase, _ = get_supabase()
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
            st.session_state.authenticated = True
            st.session_state.user_email = session.user.email
            return session.user
    except Exception as e:
        logger.error(f"get_current_user error: {e}")

    return None


def refresh_user_session() -> bool:
    """
    Verify the current session is still valid.

    Returns:
        True if session is active, False if expired.
    """
    try:
        supabase, _ = get_supabase()
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
            st.session_state.authenticated = True
            return True
        # Session gone — sign out cleanly
        if st.session_state.get("user"):
            sign_out()
        return False
    except Exception as e:
        logger.error(f"Session refresh error: {e}")
        return False


def require_auth() -> bool:
    """
    Guard function for pages that require authentication.
    Shows a warning and returns False if the user is not signed in.
    """
    if not st.session_state.get("authenticated") or not st.session_state.get("user"):
        st.warning("⚠️ Please sign in to access this page.")
        return False
    if not refresh_user_session():
        st.warning("⚠️ Your session has expired. Please sign in again.")
        return False
    return True


def require_role(allowed_roles: list) -> bool:
    """
    Guard function for pages that require a specific role.

    Args:
        allowed_roles: e.g. ["producer", "admin"]
    """
    if not require_auth():
        return False
    user_role = st.session_state.get("user_role")
    if user_role not in allowed_roles:
        st.error(f"⚠️ Access denied. Required role(s): {', '.join(allowed_roles)}")
        return False
    return True

# ─────────────────────────────────────────────────────────────
# ROLE SHORTCUTS
# ─────────────────────────────────────────────────────────────
def is_producer() -> bool:
    return st.session_state.get("user_role") == "producer"

def is_merchant() -> bool:
    return st.session_state.get("user_role") == "merchant"

def is_customer() -> bool:
    return st.session_state.get("user_role") == "customer"

def is_admin() -> bool:
    return st.session_state.get("user_role") == "admin"

# ─────────────────────────────────────────────────────────────
# PROFILE HELPER
# ─────────────────────────────────────────────────────────────
def get_user_profile() -> Optional[Dict[str, Any]]:
    """
    Return the current user's profile dict from session,
    loading it from Supabase if not already cached.
    """
    if st.session_state.get("profile"):
        return st.session_state.profile

    user = get_current_user()
    if not user:
        return None

    try:
        supabase, _ = get_supabase()
        response = supabase.table("profiles").select("*").eq("id", user.id).execute()
        if response and response.data:
            st.session_state.profile = response.data[0]
            st.session_state.user_role = response.data[0].get("role", "customer")
            return st.session_state.profile
    except Exception as e:
        logger.error(f"Profile load error: {e}")

    return None
