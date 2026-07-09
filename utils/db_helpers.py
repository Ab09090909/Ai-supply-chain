import streamlit as st
from datetime import datetime
import uuid

# ==========================================
# LAZY IMPORTS (Prevents startup crashes)
# ==========================================

def get_supabase():
    """Initialize Supabase client only when needed"""
    from src.db import get_client
    return get_client()

def hash_password(password: str):
    from utils.auth import hash_password
    return hash_password(password)

def verify_password(password: str, stored_hash: str):
    from utils.auth import verify_password
    return verify_password(password, stored_hash)

def generate_session_token():
    from utils.auth import generate_session_token
    return generate_session_token()

# ==========================================
# USER OPERATIONS
# ==========================================

def create_user(name: str, email: str, password: str, role: str, phone: str = "", company_name: str = "") -> tuple:
    supabase = get_supabase()
    try:
        response = supabase.table('users').select('id').eq('email', email).execute()
        if response.data:
            return False, "Email already registered", None
        
        pwd_hash = hash_password(password)
        
        user_response = supabase.table('users').insert({
            'name': name, 'email': email, 'password_hash': pwd_hash,
            'role': role, 'phone': phone, 'company_name': company_name, 'is_verified': True
        }).execute()
        
        if not user_response.data:
            return False, "Failed to create user", None
            
        user_id = user_response.data[0]['id']
        
        supabase.table('wallets').insert({'user_id': user_id, 'balance': 0.0}).execute()
        log_activity(user_id, "account_created", f"New {role} account created")
        
        return True, "Account created successfully!", user_id
    except Exception as e:
        return False, f"Error: {str(e)}", None

def authenticate_user(email: str, password: str) -> tuple:
    supabase = get_supabase()
    try:
        response = supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
        if not response.data:
            return False, "Invalid email or password", None
        
        user = response.data[0]
        if not verify_password(password, user['password_hash']):
            return False, "Invalid email or password", None
        
        supabase.table('users').update({'last_login': datetime.now().isoformat()}).eq('id', user['id']).execute()
        
        user_info = {
            'id': user['id'], 'name': user['name'], 'email': user['email'],
            'role': user['role'], 'session_token': generate_session_token()
        }
        return True, "Login successful!", user_info
    except Exception as e:
        return False, f"Error: {str(e)}", None

# ==========================================
# PRODUCT OPERATIONS
# ==========================================

def create_product(name: str, description: str, category: str, price: float,
                   cost_price: float, stock_quantity: int, producer_id: str, weight: float = 0) -> tuple:
    supabase = get_supabase()
    try:
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        
        response = supabase.table('products').insert({
            'name': name, 'description': description, 'category': category,
            'price': price, 'cost_price': cost_price, 'stock_quantity': stock_quantity,
            'producer_id': producer_id, 'sku': sku, 'weight': weight, 'min_stock': 10
        }).execute()
        
        if not response.data:
            return False, "Failed to create product", None
            
        log_activity(producer_id, "product_created", f"Product '{name}' created")
        return True, "Product created successfully!", response.data[0]['id']
    except Exception as e:
        return False, f"Error: {str(e)}", None

def get_products(producer_id: str = None, category: str = None, active_only: bool = True, limit: int = 100):
    supabase = get_supabase()
    try:
        query = supabase.table('products').select('*').limit(limit)
        if producer_id: 
            query = query.eq('producer_id', producer_id)
        if category: 
            query = query.eq('category', category)
        # Remove is_active filter if column doesn't exist
        # if active_only: 
        #     query = query.eq('is_active', True)
        query = query.order('created_at', desc=True)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []

def get_low_stock_products(producer_id: str = None):
    supabase = get_supabase()
    try:
        query = supabase.table('products').select('*')
        if producer_id: 
            query = query.eq('producer_id', producer_id)
        response = query.execute()
        
        if not response.data: 
            return []
        
        # Filter in Python instead of database
        low_stock = []
        for p in response.data:
            stock = p.get('quantity', p.get('stock_quantity', 0))
            min_stock = p.get('min_stock', 10)
            if stock <= min_stock:
                low_stock.append(p)
        
        return low_stock
    except Exception as e:
        st.error(f"Error fetching low stock: {e}")
        return []

# ==========================================
# ORDER OPERATIONS
# ==========================================

def get_orders(user_id: str, role: str, status: str = None, limit: int = 50):
    supabase = get_supabase()
    try:
        query = supabase.table('orders').select('*').limit(limit).order('created_at', desc=True)
        
        if role == 'customer': query = query.eq('customer_id', user_id)
        elif role == 'merchant': query = query.eq('merchant_id', user_id)
        elif role == 'producer': 
            # For producer, we need to join with products to filter by producer_id
            # Since Supabase doesn't support complex joins easily in one call, 
            # we fetch all orders and filter by product_id in a second step if needed.
            # For simplicity, we'll fetch orders where merchant_id matches (assuming producer is merchant here)
            # OR we fetch products first. Let's fetch products first.
            prod_response = supabase.table('products').select('id').eq('producer_id', user_id).execute()
            prod_ids = [p['id'] for p in prod_response.data] if prod_response.data else []
            if not prod_ids: return []
            query = query.in_('product_id', prod_ids)
            
        if status: query = query.eq('status', status)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        return []

# ==========================================
# DASHBOARD ANALYTICS
# ==========================================

# Find and replace these column references in get_dashboard_stats function:

def get_dashboard_stats(role: str, user_id: str):
    supabase = get_supabase()
    stats = {}
    
    try:
        if role == 'producer':
            # Use correct column names - Supabase might use 'quantity' instead of 'stock_quantity'
            prod_resp = supabase.table('products').select('*').eq('producer_id', user_id).execute()
            products = prod_resp.data if prod_resp.data else []
            
            # Filter active products (check if column exists)
            active_products = [p for p in products if p.get('is_active', True)]
            stats['total_products'] = len(active_products)
            
            # Check for low stock (use 'quantity' or 'stock_quantity')
            low_stock = [p for p in active_products 
                        if p.get('quantity', p.get('stock_quantity', 100)) <= p.get('min_stock', 10)]
            stats['low_stock'] = len(low_stock)
            
            # Get orders for producer's products
            prod_ids = [p['id'] for p in products]
            if prod_ids:
                order_resp = supabase.table('orders').select('*').in_('product_id', prod_ids).execute()
                orders = order_resp.data if order_resp.data else []
                stats['total_orders'] = len(orders)
                stats['revenue'] = sum(o.get('total_amount', 0) for o in orders 
                                      if o.get('status') not in ['cancelled', 'refunded'])
            else:
                stats['total_orders'] = 0
                stats['revenue'] = 0.0
                
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        # Return default values on error
        stats = {'total_products': 0, 'low_stock': 0, 'total_orders': 0, 'revenue': 0.0}
        
    return stats

# ==========================================
# ACTIVITY LOG
# ==========================================

def log_activity(user_id: str, action: str, details: str = ""):
    try:
        supabase = get_supabase()
        supabase.table('activity_log').insert({
            'user_id': user_id, 'action': action, 'details': details
        }).execute()
    except:
        pass

def check_and_fix_columns():
    """Check if required columns exist in Supabase"""
    supabase = get_supabase()
    
    try:
        # Try to get products table structure
        response = supabase.table('products').select('*').limit(1).execute()
        if response.data:
            columns = list(response.data[0].keys())
            print(f"Available columns in products table: {columns}")
            return columns
    except Exception as e:
        st.error(f"Error checking columns: {e}")
    return []
