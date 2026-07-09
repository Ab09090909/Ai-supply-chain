import streamlit as st
from datetime import datetime
import uuid

# LAZY IMPORT: Only load when function is called
def get_supabase():
    from src.db import get_client
    return get_client()

def create_user(name: str, email: str, password: str, role: str, phone: str = "", company_name: str = "") -> tuple:
    from utils.auth import hash_password
    supabase = get_supabase()
    
    try:
        # Check if email exists
        response = supabase.table('users').select('id').eq('email', email).execute()
        if response.data:
            return False, "Email already registered", None
        
        password_hash = hash_password(password)
        
        # Insert user
        user_response = supabase.table('users').insert({
            'name': name, 'email': email, 'password_hash': password_hash,
            'role': role, 'phone': phone, 'company_name': company_name, 'is_verified': True
        }).execute()
        
        if not user_response.data:
            return False, "Failed to create user", None
            
        user_id = user_response.data[0]['id']
        
        # Create wallet
        supabase.table('wallets').insert({'user_id': user_id, 'balance': 0.0}).execute()
        
        return True, "Account created successfully!", user_id
    except Exception as e:
        return False, f"Error: {str(e)}", None

def authenticate_user(email: str, password: str) -> tuple:
    from utils.auth import verify_password, generate_session_token
    supabase = get_supabase()
    
    try:
        response = supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
        if not response.data:
            return False, "Invalid email or password", None
        
        user = response.data[0]
        if not verify_password(password, user['password_hash']):
            return False, "Invalid email or password", None
        
        # Update last login
        supabase.table('users').update({'last_login': datetime.now().isoformat()}).eq('id', user['id']).execute()
        
        user_info = {
            'id': user['id'], 'name': user['name'], 'email': user['email'],
            'role': user['role'], 'session_token': generate_session_token()
        }
        return True, "Login successful!", user_info
    except Exception as e:
        return False, f"Error: {str(e)}", None

def log_activity(user_id: str, action: str, details: str = ""):
    try:
        supabase = get_supabase()
        supabase.table('activity_log').insert({'user_id': user_id, 'action': action, 'details': details}).execute()
    except:
        pass
