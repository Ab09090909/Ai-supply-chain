import streamlit as st
import hashlib
import re
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

# Rate limiting storage
login_attempts: Dict[str, list] = {}

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = stored_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False

def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format"""
    if not email:
        return False, "Email is required"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
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

def check_rate_limit(username: str, max_attempts: int = 5, lockout_time: int = 900) -> tuple[bool, str]:
    """Check if user is rate limited"""
    current_time = time.time()
    
    if username not in login_attempts:
        login_attempts[username] = []
    
    # Clean old attempts (older than lockout time)
    login_attempts[username] = [
        attempt for attempt in login_attempts[username] 
        if current_time - attempt < lockout_time
    ]
    
    if len(login_attempts[username]) >= max_attempts:
        remaining_time = lockout_time - (current_time - login_attempts[username][0])
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        return False, f"Too many failed attempts. Try again in {minutes}m {seconds}s"
    
    return True, ""

def record_login_attempt(username: str, success: bool):
    """Record login attempt for rate limiting"""
    if not success:
        current_time = time.time()
        if username not in login_attempts:
            login_attempts[username] = []
        login_attempts[username].append(current_time)

def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'remember_me' not in st.session_state:
        st.session_state.remember_me = False
    if 'logout_confirmation' not in st.session_state:
        st.session_state.logout_confirmation = False

def login_user(username: str, password: str, remember_me: bool = False) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Login user with validation and rate limiting
    Returns: (success, message, user_info)
    """
    # Check rate limit
    is_allowed, message = check_rate_limit(username)
    if not is_allowed:
        return False, message, None
    
    # Validate inputs
    email_valid, email_msg = validate_email(username)
    if not email_valid:
        return False, email_msg, None
    
    # Check if user exists
    if 'users' not in st.session_state:
        st.session_state.users = {}
    
    if username not in st.session_state.users:
        record_login_attempt(username, False)
        return False, "Invalid email or password", None
    
    user_data = st.session_state.users[username]
    
    # Verify password
    if not verify_password(password, user_data['password']):
        record_login_attempt(username, False)
        return False, "Invalid email or password", None
    
    # Successful login - clear rate limit
    if username in login_attempts:
        del login_attempts[username]
    
    # Generate session token
    session_token = generate_session_token()
    
    # Update user info
    user_info = {
        'email': username,
        'name': user_data['name'],
        'role': user_data['role'],
        'session_token': session_token,
        'last_login': datetime.now().isoformat()
    }
    
    # Set session state
    st.session_state.authenticated = True
    st.session_state.user_info = user_info
    st.session_state.session_token = session_token
    st.session_state.remember_me = remember_me
    
    return True, "Login successful!", user_info

def register_user(name: str, email: str, password: str, role: str) -> tuple[bool, str]:
    """
    Register new user with validation
    Returns: (success, message)
    """
    # Validate inputs
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
    
    # Initialize users dict if not exists
    if 'users' not in st.session_state:
        st.session_state.users = {}
    
    # Check if user already exists
    if email in st.session_state.users:
        return False, "Email already registered"
    
    # Create new user
    st.session_state.users[email] = {
        'name': name.strip(),
        'email': email,
        'password': hash_password(password),
        'role': role,
        'created_at': datetime.now().isoformat()
    }
    
    return True, "Registration successful! Please login."

def forgot_password(email: str) -> tuple[bool, str]:
    """
    Handle forgot password request
    Returns: (success, message)
    """
    email_valid, email_msg = validate_email(email)
    if not email_valid:
        return False, email_msg
    
    if 'users' not in st.session_state or email not in st.session_state.users:
        # Don't reveal if email exists for security
        return True, "If the email exists, a password reset link has been sent."
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store reset token (in production, send via email)
    if 'password_resets' not in st.session_state:
        st.session_state.password_resets = {}
    
    st.session_state.password_resets[email] = {
        'token': reset_token,
        'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
    }
    
    # In production, send email with reset_token
    # For demo, show the token
    return True, f"Password reset token (demo): {reset_token}\n\nIn production, this would be sent via email."

def reset_password(email: str, token: str, new_password: str) -> tuple[bool, str]:
    """
    Reset password using token
    Returns: (success, message)
    """
    if 'password_resets' not in st.session_state or email not in st.session_state.password_resets:
        return False, "Invalid reset request"
    
    reset_data = st.session_state.password_resets[email]
    
    # Verify token
    if reset_data['token'] != token:
        return False, "Invalid reset token"
    
    # Check expiration
    expires_at = datetime.fromisoformat(reset_data['expires_at'])
    if datetime.now() > expires_at:
        del st.session_state.password_resets[email]
        return False, "Reset token has expired"
    
    # Validate new password
    password_valid, password_msg = validate_password(new_password)
    if not password_valid:
        return False, password_msg
    
    # Update password
    st.session_state.users[email]['password'] = hash_password(new_password)
    
    # Remove used token
    del st.session_state.password_resets[email]
    
    return True, "Password reset successful! Please login with your new password."

def logout_user():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.session_token = None
    st.session_state.logout_confirmation = False
    st.rerun()

def require_auth():
    """Decorator to require authentication"""
    if not st.session_state.authenticated:
        st.warning("Please login to access this page")
        st.stop()
