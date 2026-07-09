import streamlit as st
import re
import time
import hashlib
import secrets
from typing import Dict

login_attempts: Dict[str, list] = {}

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, pwd_hash = stored_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False

def validate_email(email: str) -> tuple:
    if not email: return False, "Email is required"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email): return False, "Invalid email format"
    return True, ""

def validate_password(password: str) -> tuple:
    if not password: return False, "Password is required"
    if len(password) < 8: return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password): return False, "Must contain uppercase"
    if not re.search(r'[a-z]', password): return False, "Must contain lowercase"
    if not re.search(r'\d', password): return False, "Must contain number"
    if not re.search(r'[!@#$%^&*]', password): return False, "Must contain special char"
    return True, ""

def check_rate_limit(username: str) -> tuple:
    current_time = time.time()
    if username not in login_attempts: login_attempts[username] = []
    login_attempts[username] = [a for a in login_attempts[username] if current_time - a < 900]
    if len(login_attempts[username]) >= 5:
        return False, "Too many attempts. Try again in 15m"
    return True, ""

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def initialize_session_state():
    defaults = {'authenticated': False, 'user_info': None, 'session_token': None, 'logout_confirmation': False}
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

def login_user(email: str, password: str, remember_me: bool = False) -> tuple:
    # LAZY IMPORT
    from utils.db_helpers import authenticate_user
    
    is_allowed, message = check_rate_limit(email)
    if not is_allowed: return False, message, None
    
    email_valid, email_msg = validate_email(email)
    if not email_valid: return False, email_msg, None
    
    success, message, user_info = authenticate_user(email, password)
    
    if success:
        if email in login_attempts: del login_attempts[email]
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.session_token = user_info['session_token']
        return True, message, user_info
    else:
        if email not in login_attempts: login_attempts[email] = []
        login_attempts[email].append(time.time())
        return False, message, None

def register_user(name: str, email: str, password: str, role: str) -> tuple:
    # LAZY IMPORT
    from utils.db_helpers import create_user
    
    if not name: return False, "Name is required"
    email_valid, email_msg = validate_email(email)
    if not email_valid: return False, email_msg
    password_valid, password_msg = validate_password(password)
    if not password_valid: return False, password_msg
    
    success, message, user_id = create_user(name.strip(), email, password, role)
    return success, message

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.session_token = None
    st.rerun()
