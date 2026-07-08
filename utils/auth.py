"""Authentication utilities for Supabase."""
import streamlit as st
import logging
from typing import Optional, Tuple, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# LAZY IMPORT to avoid circular imports
# ─────────────────────────────────────────────────────────────
def get_supabase():
    """Lazy load supabase client to avoid circular imports."""
    from utils.db_helpers import supabase, clear_data_cache
    return supabase, clear_data_cache

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def sign_up(email: str, password: str, full_name: str, role: str, region: str, phone: str = "") -> Tuple[bool, str]:
    """
    Register a new user.
    
    Args:
        email: User's email address
        password: User's password (min 8 characters)
        full_name: User's full name
        role: User role (producer, merchant, customer, admin)
        region: User's region
        phone: Optional phone number
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Validate inputs
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        
        if not email or '@' not in email:
            return False, "Please enter a valid email address."
        
        if not full_name or len(full_name.strip()) < 2:
            return False, "Please enter your full name."
        
        supabase, _ = get_supabase()
        
        # Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": role,
                    "region": region,
                }
            }
        })
        
        if response and response.user:
            user_id = response.user.id
            
            # Create profile
            profile_data = {
                "id": user_id,
                "full_name": full_name.strip(),
                "role": role.lower(),
                "region": region,
                "phone": phone.strip() if phone else None,
                "is_verified": False,
                "documents_uploaded": False,
                "created_at": "now()",
                "updated_at": "now()"
            }
            
            # Insert profile
            try:
                supabase.table("profiles").insert(profile_data).execute()
                logger.info(f"User registered successfully: {email} with role: {role}")
                return True, "Account created successfully! Please check your email to verify your account."
            except Exception as e:
                logger.error(f"Profile creation error for {email}: {e}")
                # Try to clean up auth user if profile creation fails
                try:
                    supabase.auth.admin.delete_user(user_id)
                except Exception:
                    pass
                return False, f"Failed to create user profile: {str(e)}"
        else:
            logger.warning(f"Signup failed for {email}: No user returned")
            return False, "Signup failed. Please try again."
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Signup error for {email}: {error_msg}")
        
        if "already registered" in error_msg.lower():
            return False, "This email is already registered. Please sign in."
        elif "password" in error_msg.lower():
            return False, "Password does not meet security requirements. Please use at least 8 characters."
        else:
            return False, f"Registration error: {error_msg}"

def sign_in(email: str, password: str) -> Tuple[bool, str]:
    """
    Sign in an existing user.
    
    Args:
        email: User's email address
        password: User's password
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        if not email or not password:
            return False, "Please enter both email and password."
        
        supabase, clear_data_cache = get_supabase()
        
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        
        if response and response.user:
            # Set session state
            st.session_state.user = response.user
            st.session_state.authenticated = True
            st.session_state.user_email = response.user.email
            
            # Clear cache for fresh data
            clear_data_cache()
            
            # Load profile
            try:
                profile_response = supabase.table("profiles").select("*").eq("id", response.user.id).execute()
                if profile_response and profile_response.data:
                    st.session_state.profile = profile_response.data[0]
                    st.session_state.user_role = profile_response.data[0].get('role', 'customer')
                    logger.info(f"User signed in: {email} as {st.session_state.user_role}")
                else:
                    # Profile missing - create one
                    logger.warning(f"Profile missing for {email}, creating default")
                    default_name = email.split('@')[0]
                    profile_data = {
                        "id": response.user.id,
                        "full_name": default_name,
                        "role": "customer",
                        "region": "Addis Ababa",
                        "is_verified": False,
                        "documents_uploaded": False
                    }
                    supabase.table("profiles").insert(profile_data).execute()
                    # Reload profile
                    profile_response = supabase.table("profiles").select("*").eq("id", response.user.id).execute()
                    if profile_response and profile_response.data:
                        st.session_state.profile = profile_response.data[0]
                        st.session_state.user_role = "customer"
            except Exception as e:
                logger.error(f"Profile loading error for {email}: {e}")
                # Continue even if profile load fails, we'll try again later
            
            return True, "Signed in successfully!"
        else:
            logger.warning(f"Login failed for {email}: Invalid credentials")
            return False, "Invalid email or password. Please try again."
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Login error for {email}: {error_msg}")
        
        if "Invalid login credentials" in error_msg:
            return False, "Invalid email or password. Please try again."
        elif "email not confirmed" in error_msg.lower():
            return False, "Please verify your email address before signing in. Check your inbox for the verification link."
        else:
            return False, f"Login error: {error_msg}"

def sign_out() -> None:
    """Sign out the current user and clear session state."""
    try:
        supabase, clear_data_cache = get_supabase()
        supabase.auth.sign_out()
    except Exception as e:
        logger.error(f"Sign out error: {e}")
    
    # Clear all session state
    session_keys = [
        'user', 'profile', 'authenticated', 'user_role', 
        'user_email', 'auth_redirect', 'nav_clicked'
    ]
    for key in session_keys:
        if key in st.session_state:
            st.session_state[key] = None
    
    # Clear cache
    try:
        clear_data_cache()
    except Exception:
        pass
    
    logger.info("User signed out")

def forgot_password(email: str) -> Tuple[bool, str]:
    """
    Send password reset email.
    
    Args:
        email: User's registered email address
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        if not email or '@' not in email:
            return False, "Please enter a valid email address."
        
        supabase, _ = get_supabase()
        
        # Check if user exists
        try:
            # Try to find user by email
            response = supabase.table("profiles").select("id").eq("email", email).execute()
            if not response or not response.data:
                # Check auth users (we'll use a different approach)
                pass
        except Exception:
            # Continue even if check fails
            pass
        
        # Send reset email
        supabase.auth.reset_password_for_email(email)
        logger.info(f"Password reset email sent to: {email}")
        return True, "Password reset link sent to your email. Please check your inbox (and spam folder)."
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Password reset error for {email}: {error_msg}")
        
        if "not found" in error_msg.lower():
            return False, "No account found with this email address."
        else:
            return False, f"Failed to send reset email: {error_msg}"

def get_current_user() -> Optional[Any]:
    """
    Get the current authenticated user.
    
    Returns:
        Optional[User]: Current user object or None if not authenticated
    """
    # Check session state first
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
        logger.error(f"Get current user error: {e}")
    
    return None

def refresh_user_session() -> bool:
    """
    Refresh the user session.
    
    Returns:
        bool: True if session is valid, False otherwise
    """
    try:
        supabase, _ = get_supabase()
        session = supabase.auth.get_session()
        
        if session and session.user:
            st.session_state.user = session.user
            st.session_state.authenticated = True
            return True
        else:
            # Session expired or invalid
            if st.session_state.get("user"):
                # Clear invalid session
                sign_out()
            return False
    except Exception as e:
        logger.error(f"Session refresh error: {e}")
        return False

def require_auth() -> bool:
    """
    Decorator-like function to check if user is authenticated.
    Returns False and shows warning if not authenticated.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if not st.session_state.get("authenticated") or not st.session_state.get("user"):
        st.warning("⚠️ Please sign in to access this page.")
        return False
    
    # Refresh session
    if not refresh_user_session():
        st.warning("⚠️ Your session has expired. Please sign in again.")
        return False
    
    return True

def require_role(allowed_roles: list) -> bool:
    """
    Check if current user has one of the allowed roles.
    
    Args:
        allowed_roles: List of allowed role names
    
    Returns:
        bool: True if user has allowed role, False otherwise
    """
    if not require_auth():
        return False
    
    user_role = st.session_state.get("user_role")
    if user_role not in allowed_roles:
        st.error(f"⚠️ Access denied. This page requires one of these roles: {', '.join(allowed_roles)}")
        return False
    
    return True

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS FOR SPECIFIC ROLES
# ─────────────────────────────────────────────────────────────

def is_producer() -> bool:
    """Check if current user is a producer."""
    return st.session_state.get("user_role") == "producer"

def is_merchant() -> bool:
    """Check if current user is a merchant."""
    return st.session_state.get("user_role") == "merchant"

def is_customer() -> bool:
    """Check if current user is a customer."""
    return st.session_state.get("user_role") == "customer"

def is_admin() -> bool:
    """Check if current user is an admin."""
    return st.session_state.get("user_role") == "admin"

def get_user_profile() -> Optional[Dict[str, Any]]:
    """
    Get current user's profile from session state.
    If not loaded, try to load it.
    
    Returns:
        Optional[Dict]: User profile or None
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
            st.session_state.user_role = response.data[0].get('role', 'customer')
            return st.session_state.profile
    except Exception as e:
        logger.error(f"Profile load error: {e}")
    
    return None
