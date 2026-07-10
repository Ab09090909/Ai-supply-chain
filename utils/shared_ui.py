import streamlit as st
from datetime import datetime
import uuid

def get_supabase():
    """Get Supabase client"""
    from src.db import get_client
    return get_client()

def hash_password(password: str) -> str:
    """Simple password hash (use bcrypt in production)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == stored_hash

def generate_session_token() -> str:
    """Generate unique session token"""
    return str(uuid.uuid4())

# ==========================================
# USER OPERATIONS
# ==========================================

def register_user(name: str, email: str, password: str, role: str, 
                  phone: str = "", company_name: str = "", region: str = "Addis Ababa") -> tuple:
    """Register a new user"""
    supabase = get_supabase()
    if not supabase:
        return False, "Database connection failed", None
    
    try:
        # Check if email exists
        response = supabase.table('users').select('id').eq('email', email).execute()
        if response.data and len(response.data) > 0:
            return False, "Email already registered", None
        
        # Create user
        user_data = {
            'name': name,
            'email': email,
            'password_hash': hash_password(password),
            'role': role,
            'phone': phone,
            'company_name': company_name,
            'region': region,
            'is_verified': True,  # Auto-verify for testing
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if not result.data:
            return False, "Failed to create user", None
        
        user_id = result.data[0]['id']
        
        # Create wallet for user
        supabase.table('wallets').insert({
            'user_id': user_id,
            'balance': 0.0
        }).execute()
        
        return True, "Account created successfully!", user_id
        
    except Exception as e:
        return False, f"Error: {str(e)}", None

def login_user(email: str, password: str) -> tuple:
    """Authenticate user and return user info"""
    supabase = get_supabase()
    if not supabase:
        return False, "Database connection failed", None
    
    try:
        # Find user by email
        response = supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "Invalid email or password", None
        
        user = response.data[0]
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return False, "Invalid email or password", None
        
        # Update last login
        supabase.table('users').update({
            'last_login': datetime.now().isoformat()
        }).eq('id', user['id']).execute()
        
        # Prepare user info for session
        user_info = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'phone': user.get('phone', ''),
            'company_name': user.get('company_name', ''),
            'region': user.get('region', 'Addis Ababa'),
            'session_token': generate_session_token()
        }
        
        return True, f"Welcome back, {user['name']}!", user_info
        
    except Exception as e:
        return False, f"Login error: {str(e)}", None

def update_user(user_id: str, **kwargs) -> bool:
    """Update user information"""
    supabase = get_supabase()
    if not supabase:
        return False
    
    try:
        allowed_fields = ['name', 'email', 'phone', 'company_name', 'region', 'address']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.now().isoformat()
        
        result = supabase.table('users').update(updates).eq('id', user_id).execute()
        return result.data is not None
    except Exception as e:
        st.error(f"Error updating user: {e}")
        return False

# ==========================================
# PRODUCT OPERATIONS
# ==========================================

def create_product(name: str, description: str, category: str, price: float,
                   cost_price: float, stock_quantity: int, producer_id: str,
                   weight: float = 0, image_url: str = None, image_base64: str = None,
                   min_stock: int = 10) -> tuple:
    """Create a new product"""
    supabase = get_supabase()
    if not supabase:
        return False, "Database connection failed", None
    
    try:
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        
        product_data = {
            'name': name,
            'description': description,
            'category': category,
            'price': price,
            'cost_price': cost_price,
            'quantity': stock_quantity,
            'min_stock': min_stock,
            'producer_id': producer_id,
            'sku': sku,
            'weight': weight,
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
        
        if image_url:
            product_data['image_url'] = image_url
        if image_base64:
            product_data['image_base64'] = image_base64
        
        result = supabase.table('products').insert(product_data).execute()
        
        if not result.data:
            return False, "Failed to create product", None
        
        return True, "Product created successfully!", result.data[0]['id']
        
    except Exception as e:
        return False, f"Error: {str(e)}", None

def get_products(producer_id: str = None, category: str = None, 
                 active_only: bool = True, limit: int = 100):
    """Get products with optional filters"""
    supabase = get_supabase()
    if not supabase:
        return []
    
    try:
        query = supabase.table('products').select('*').limit(limit)
        
        if producer_id:
            query = query.eq('producer_id', producer_id)
        if category:
            query = query.eq('category', category)
        if active_only:
            query = query.eq('is_active', True)
        
        query = query.order('created_at', desc=True)
        result = query.execute()
        
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []

def update_product(product_id: str, **kwargs) -> tuple:
    """Update product information"""
    supabase = get_supabase()
    if not supabase:
        return False, "Database connection failed"
    
    try:
        allowed_fields = ['name', 'description', 'category', 'price', 'cost_price', 
                         'quantity', 'min_stock', 'weight', 'image_url', 'image_base64', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False, "No valid fields to update"
        
        updates['updated_at'] = datetime.now().isoformat()
        
        result = supabase.table('products').update(updates).eq('id', product_id).execute()
        
        if result.data:
            return True, "Product updated successfully!"
        return False, "Failed to update product"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_product(product_id: str) -> tuple:
    """Delete a product"""
    supabase = get_supabase()
    if not supabase:
        return False, "Database connection failed"
    
    try:
        result = supabase.table('products').delete().eq('id', product_id).execute()
        
        if result.data is not None:
            return True, "Product deleted successfully!"
        return False, "Failed to delete product"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_low_stock_products(producer_id: str = None):
    """Get products with low stock"""
    supabase = get_supabase()
    if not supabase:
        return []
    
    try:
        query = supabase.table('products').select('*')
        
        if producer_id:
            query = query.eq('producer_id', producer_id)
        
        result = query.execute()
        products = result.data if result.data else []
        
        # Filter products where quantity <= min_stock
        low_stock = [p for p in products if p.get('quantity', 0) <= p.get('min_stock', 10)]
        
        return low_stock
    except Exception as e:
        st.error(f"Error fetching low stock products: {e}")
        return []

# ==========================================
# ORDER OPERATIONS
# ==========================================

def get_orders(user_id: str, role: str, status: str = None, limit: int = 50):
    """Get orders based on user role"""
    supabase = get_supabase()
    if not supabase:
        return []
    
    try:
        query = supabase.table('orders').select('*').limit(limit).order('created_at', desc=True)
        
        if role == 'customer':
            query = query.eq('customer_id', user_id)
        elif role == 'merchant':
            query = query.eq('merchant_id', user_id)
        elif role == 'producer':
            # Get producer's products first
            prod_response = supabase.table('products').select('id').eq('producer_id', user_id).execute()
            prod_ids = [p['id'] for p in prod_response.data] if prod_response.data else []
            if not prod_ids:
                return []
            query = query.in_('product_id', prod_ids)
        
        if status:
            query = query.eq('status', status)
        
        result = query.execute()
        return result.data if result.data else []
        
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        return []

# ==========================================
# DASHBOARD STATS
# ==========================================

def get_dashboard_stats(role: str, user_id: str):
    """Get dashboard statistics"""
    supabase = get_supabase()
    if not supabase:
        return {'total_products': 0, 'low_stock': 0, 'total_orders': 0, 'revenue': 0.0}
    
    stats = {'total_products': 0, 'low_stock': 0, 'total_orders': 0, 'revenue': 0.0}
    
    try:
        if role == 'producer':
            # Get products
            prod_response = supabase.table('products').select('*').eq('producer_id', user_id).execute()
            products = prod_response.data if prod_response.data else []
            
            stats['total_products'] = len(products)
            stats['low_stock'] = len([p for p in products if p.get('quantity', 0) <= p.get('min_stock', 10)])
            
            # Get orders for producer's products
            prod_ids = [p['id'] for p in products]
            if prod_ids:
                order_response = supabase.table('orders').select('*').in_('product_id', prod_ids).execute()
                orders = order_response.data if order_response.data else []
                
                stats['total_orders'] = len(orders)
                stats['revenue'] = sum(
                    o.get('total_amount', 0) for o in orders 
                    if o.get('status') not in ['cancelled', 'refunded']
                )
        
        return stats
        
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return stats

# ==========================================
# AI CONTEXT OPERATIONS
# ==========================================
def get_ai_context(user_id: str, role: str) -> str:
    """Generate a real-time context string for the AI assistant based on user data."""
    try:
        if role == 'producer':
            stats = get_dashboard_stats(role, user_id)
            context_parts = [
                f"Total Products: {stats['total_products']}",
                f"Low Stock Items: {stats['low_stock']}",
                f"Total Orders: {stats['total_orders']}",
                f"Total Revenue: ${stats['revenue']:.2f}"
            ]
            
            # Fetch specific low stock items to warn the AI
            low_stock_items = get_low_stock_products(user_id)
            if low_stock_items:
                names = [f"{item['name']} (Qty: {item['quantity']})" for item in low_stock_items[:3]]
                context_parts.append(f"Critical Low Stock Alerts: {', '.join(names)}")
                
            return " | ".join(context_parts)
            
        elif role == 'merchant':
            orders = get_orders(user_id, role, limit=5)
            return f"Recent Orders Count: {len(orders)} | Role: Merchant"
            
        elif role == 'customer':
            orders = get_orders(user_id, role, limit=5)
            return f"Recent Orders Count: {len(orders)} | Role: Customer"
            
        elif role == 'admin':
            return "Role: Admin | Has access to system-wide insights."
            
        return "No specific data available."
    except Exception as e:
        return f"Error fetching context: {str(e)}"
