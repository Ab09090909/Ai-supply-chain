import streamlit as st
from src.db import get_client
from utils.auth import hash_password, verify_password, generate_session_token
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

supabase = get_client()

# =====================================================
# USER OPERATIONS
# =====================================================

def create_user(name: str, email: str, password: str, role: str, 
                phone: str = "", company_name: str = "") -> tuple:
    """Create a new user with wallet"""
    try:
        # Check if email exists
        response = supabase.table('users').select('id').eq('email', email).execute()
        if response.data:
            return False, "Email already registered", None
        
        password_hash = hash_password(password)
        
        # Insert user
        user_response = supabase.table('users').insert({
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'phone': phone,
            'company_name': company_name,
            'is_verified': True
        }).execute()
        
        if not user_response.data:
            return False, "Failed to create user", None
            
        user_id = user_response.data[0]['id']
        
        # Create wallet
        supabase.table('wallets').insert({
            'user_id': user_id,
            'balance': 0.0
        }).execute()
        
        log_activity(user_id, "account_created", f"New {role} account created")
        
        return True, "Account created successfully!", user_id
    
    except Exception as e:
        return False, f"Error creating account: {str(e)}", None


def authenticate_user(email: str, password: str) -> tuple:
    """Authenticate user and return user info"""
    try:
        response = supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
        
        if not response.data:
            return False, "Invalid email or password", None
        
        user = response.data[0]
        
        if not verify_password(password, user['password_hash']):
            return False, "Invalid email or password", None
        
        # Update last login
        supabase.table('users').update({
            'last_login': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }).eq('id', user['id']).execute()
        
        log_activity(user['id'], "login", "User logged in")
        
        user_info = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'phone': user.get('phone', ''),
            'company_name': user.get('company_name', ''),
            'session_token': generate_session_token()
        }
        
        return True, "Login successful!", user_info
    
    except Exception as e:
        return False, f"Authentication error: {str(e)}", None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    return response.data[0] if response.data else None


def get_all_users(role: str = None, limit: int = 100) -> List[Dict]:
    """Get all users, optionally filtered by role"""
    query = supabase.table('users').select('*').order('created_at', desc=True).limit(limit)
    if role:
        query = query.eq('role', role)
    
    response = query.execute()
    return response.data if response.data else []


# =====================================================
# PRODUCT OPERATIONS
# =====================================================

def create_product(name: str, description: str, category: str, price: float,
                   cost_price: float, stock_quantity: int, producer_id: str,
                   weight: float = 0) -> tuple:
    """Create a new product"""
    try:
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        
        response = supabase.table('products').insert({
            'name': name,
            'description': description,
            'category': category,
            'price': price,
            'cost_price': cost_price,
            'stock_quantity': stock_quantity,
            'producer_id': producer_id,
            'sku': sku,
            'weight': weight
        }).execute()
        
        if not response.data:
            return False, "Failed to create product", None
            
        product_id = response.data[0]['id']
        
        log_activity(producer_id, "product_created", f"Product '{name}' created (SKU: {sku})")
        return True, "Product created successfully!", product_id
    
    except Exception as e:
        return False, f"Error creating product: {str(e)}", None


def get_products(producer_id: str = None, category: str = None, 
                 active_only: bool = True, limit: int = 100) -> List[Dict]:
    """Get products with optional filters"""
    query = supabase.table('products').select('*').limit(limit)
    
    if producer_id:
        query = query.eq('producer_id', producer_id)
    if category:
        query = query.eq('category', category)
    if active_only:
        query = query.eq('is_active', True)
        
    query = query.order('created_at', desc=True)
    response = query.execute()
    
    return response.data if response.data else []


def update_product_stock(product_id: str, quantity_change: int) -> bool:
    """Update product stock"""
    response = supabase.table('products').select('stock_quantity').eq('id', product_id).execute()
    if not response.data:
        return False
    
    current_stock = response.data[0]['stock_quantity']
    new_stock = current_stock + quantity_change
    
    if new_stock < 0:
        return False
    
    supabase.table('products').update({
        'stock_quantity': new_stock,
        'updated_at': datetime.now().isoformat()
    }).eq('id', product_id).execute()
    
    return True


# =====================================================
# ORDER OPERATIONS
# =====================================================

def create_order(customer_id: str, merchant_id: str, product_id: str,
                 quantity: int, unit_price: float, shipping_address: str,
                 notes: str = "") -> tuple:
    """Create a new order"""
    try:
        # Check stock
        stock_response = supabase.table('products').select('stock_quantity').eq('id', product_id).execute()
        if not stock_response.data or stock_response.data[0]['stock_quantity'] < quantity:
            return False, "Insufficient stock", None
        
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        total_amount = unit_price * quantity
        
        order_response = supabase.table('orders').insert({
            'order_number': order_number,
            'customer_id': customer_id,
            'merchant_id': merchant_id,
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'shipping_address': shipping_address,
            'notes': notes
        }).execute()
        
        if not order_response.data:
            return False, "Failed to create order", None
            
        # Reduce stock
        update_product_stock(product_id, -quantity)
        
        log_activity(customer_id, "order_created", f"Order {order_number} created")
        return True, f"Order {order_number} created successfully!", order_response.data[0]['id']
    
    except Exception as e:
        return False, f"Error creating order: {str(e)}", None


def get_orders(user_id: str, role: str, status: str = None, limit: int = 50) -> List[Dict]:
    """Get orders for a user based on their role"""
    query = supabase.table('orders').select('*').limit(limit).order('created_at', desc=True)
    
    if role == 'customer':
        query = query.eq('customer_id', user_id)
    elif role == 'merchant':
        query = query.eq('merchant_id', user_id)
        
    if status:
        query = query.eq('status', status)
        
    response = query.execute()
    return response.data if response.data else []


# =====================================================
# WALLET OPERATIONS
# =====================================================

def get_wallet_balance(user_id: str) -> float:
    """Get user's wallet balance"""
    response = supabase.table('wallets').select('balance').eq('user_id', user_id).execute()
    return response.data[0]['balance'] if response.data else 0.0


def wallet_transaction(user_id: str, amount: float, trans_type: str, description: str = "") -> bool:
    """Process wallet transaction"""
    wallet_response = supabase.table('wallets').select('*').eq('user_id', user_id).execute()
    if not wallet_response.data:
        return False
    
    wallet = wallet_response.data[0]
    
    if trans_type == 'debit' and wallet['balance'] < amount:
        return False
    
    new_balance = wallet['balance'] + amount if trans_type == 'credit' else wallet['balance'] - amount
    
    # Update wallet
    supabase.table('wallets').update({
        'balance': new_balance,
        'updated_at': datetime.now().isoformat()
    }).eq('user_id', user_id).execute()
    
    # Insert transaction record
    supabase.table('transactions').insert({
        'wallet_id': wallet['id'],
        'type': trans_type,
        'amount': amount,
        'description': description,
        'balance_after': new_balance
    }).execute()
    
    return True


# =====================================================
# ACTIVITY LOG
# =====================================================

def log_activity(user_id: str, action: str, details: str = ""):
    """Log user activity"""
    try:
        supabase.table('activity_log').insert({
            'user_id': user_id,
            'action': action,
            'details': details
        }).execute()
    except:
        pass  # Don't fail main operation if logging fails
