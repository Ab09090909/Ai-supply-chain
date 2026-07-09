import streamlit as st
import re
import time
from datetime import datetime
from typing import Optional, Dict, Any
import secrets

# Rate limiting storage
login_attempts: Dict[str, list] = {}


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    import hashlib
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    import hashlib
    try:
        salt, pwd_hash = stored_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False


def validate_email(email: str) -> tuple:
    """Validate email format"""
    if not email:
        return False, "Email is required"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""


def validate_password(password: str) -> tuple:
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, ""


def check_rate_limit(username: str, max_attempts: int = 5, lockout_time: int = 900) -> tuple:
    """Check if user is rate limited"""
    current_time = time.time()
    
    if username not in login_attempts:
        login_attempts[username] = []
    
    login_attempts[username] = [
        a for a in login_attempts[username] if current_time - a < lockout_time
    ]
    
    if len(login_attempts[username]) >= max_attempts:
        remaining = lockout_time - (current_time - login_attempts[username][0])
        return False, f"Too many attempts. Try again in {int(remaining // 60)}m {int(remaining % 60)}s"
    
    return True, ""


def record_login_attempt(username: str, success: bool):
    """Record login attempt"""
    if not success:
        if username not in login_attempts:
            login_attempts[username] = []
        login_attempts[username].append(time.time())


def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)


def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'authenticated': False,
        'user_info': None,
        'session_token': None,
        'remember_me': False,
        'logout_confirmation': False,
        'current_page': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(email: str, password: str, remember_me: bool = False) -> tuple:
    """Login user using database"""
    from utils.db_helpers import authenticate_user
    
    is_allowed, message = check_rate_limit(email)
    if not is_allowed:
        return False, message, None
    
    email_valid, email_msg = validate_email(email)
    if not email_valid:
        return False, email_msg, None
    
    success, message, user_info = authenticate_user(email, password)
    
    if success:
        if email in login_attempts:
            del login_attempts[email]
        
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.session_token = user_info['session_token']
        st.session_state.remember_me = remember_me
        
        return True, message, user_info
    else:
        record_login_attempt(email, False)
        return False, message, None


def register_user(name: str, email: str, password: str, role: str) -> tuple:
    """Register user using database"""
    from utils.db_helpers import create_user
    
    if not name or not name.strip():
        return False, "Name is required"
    
    email_valid, email_msg = validate_email(email)
    if not email_valid:
        return False, email_msg
    
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        return False, password_msg
    
    if role not in ['producer', 'merchant', 'customer', 'admin']:
        return False, "Invalid role selected"
    
    success, message, user_id = create_user(name.strip(), email, password, role)
    return success, message


def logout_user():
    """Logout current user"""
    from utils.db_helpers import log_activity
    
    if st.session_state.user_info:
        log_activity(st.session_state.user_info['id'], "logout", "User logged out")
    
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.session_token = None
    st.session_state.logout_confirmation = False
    st.session_state.current_page = None
    st.rerun()
