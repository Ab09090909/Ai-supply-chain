# utils/db_helpers.py
import streamlit as st
from supabase import create_client, Client
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client with error handling
@st.cache_resource
def get_supabase_client():
    """Get Supabase client instance with proper error handling"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            st.error("❌ Supabase credentials not found in environment variables")
            return None
        
        # Create client WITHOUT proxy argument
        client = create_client(supabase_url, supabase_key)
        return client
    
    except TypeError as e:
        if 'proxy' in str(e):
            st.error("❌ Supabase client version incompatible. Please update supabase-py")
            st.info("Run: pip install --upgrade supabase")
            return None
        else:
            st.error(f"❌ Error connecting to Supabase: {e}")
            return None
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {e}")
        return None

# Global client
supabase = get_supabase_client()

# --- User Functions ---
def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.session_state.user_id = None

def authenticate_user(email, password):
    """Authenticate a user"""
    try:
        if supabase is None:
            return None, "Database connection failed"
        
        # Try to authenticate
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Get user profile from users table
            user_data = supabase.table('users')\
                .select('*')\
                .eq('email', email)\
                .execute()
            
            if user_data.data:
                user_info = user_data.data[0]
                return user_info, "success"
            else:
                return None, "User profile not found"
        else:
            return None, "Invalid credentials"
    
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return None, "Invalid email or password"
        elif "Network" in error_msg or "connect" in error_msg.lower():
            return None, "Network error. Please check your connection."
        else:
            return None, f"Login failed: {error_msg}"

def logout_user():
    """Logout the current user"""
    try:
        if supabase:
            supabase.auth.sign_out()
    except:
        pass
    
    st.session_state.authenticated = False
    st.session_state.user_info = {}
    st.session_state.user_id = None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        if supabase is None:
            return None
        
        response = supabase.table('users')\
            .select('*')\
            .eq('id', user_id)\
            .execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching user: {e}")
        return None

def update_user(user_id, **kwargs):
    """Update user information"""
    try:
        if supabase is None:
            return False, "Database connection failed"
        
        # Remove None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        response = supabase.table('users')\
            .update(update_data)\
            .eq('id', user_id)\
            .execute()
        
        if response.data:
            return True, "User updated successfully"
        return False, "User update failed"
    
    except Exception as e:
        return False, f"Error updating user: {e}"

# --- Product Functions ---
def get_products(producer_id=None, limit=100):
    """Get products, optionally filtered by producer"""
    try:
        if supabase is None:
            return []
        
        query = supabase.table('products')\
            .select('*')\
            .limit(limit)
        
        if producer_id:
            query = query.eq('producer_id', producer_id)
        
        response = query.execute()
        
        if response.data:
            return response.data
        return []
    
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []

def create_product(name, description, category, price, cost_price, stock_quantity, producer_id, weight=0.0, image_url=None):
    """Create a new product"""
    try:
        if supabase is None:
            return False, "Database connection failed", None
        
        # Generate SKU
        import uuid
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        
        product_data = {
            'name': name,
            'description': description,
            'category': category,
            'price': price,
            'cost_price': cost_price,
            'quantity': stock_quantity,
            'producer_id': producer_id,
            'weight': weight,
            'sku': sku,
            'image_url': image_url,
            'min_stock': 10,
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('products')\
            .insert(product_data)\
            .execute()
        
        if response.data:
            return True, "Product created successfully", response.data[0]['id']
        return False, "Product creation failed", None
    
    except Exception as e:
        return False, f"Error creating product: {e}", None

def update_product(product_id, **kwargs):
    """Update product information"""
    try:
        if supabase is None:
            return False, "Database connection failed"
        
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        response = supabase.table('products')\
            .update(update_data)\
            .eq('id', product_id)\
            .execute()
        
        if response.data:
            return True, "Product updated successfully"
        return False, "Product update failed"
    
    except Exception as e:
        return False, f"Error updating product: {e}"

def delete_product(product_id):
    """Delete a product"""
    try:
        if supabase is None:
            return False, "Database connection failed"
        
        response = supabase.table('products')\
            .delete()\
            .eq('id', product_id)\
            .execute()
        
        if response.data:
            return True, "Product deleted successfully"
        return False, "Product deletion failed"
    
    except Exception as e:
        return False, f"Error deleting product: {e}"

def update_product_stock(product_id, new_quantity):
    """Update product stock quantity"""
    try:
        if supabase is None:
            return False, "Database connection failed"
        
        response = supabase.table('products')\
            .update({'quantity': new_quantity})\
            .eq('id', product_id)\
            .execute()
        
        if response.data:
            return True, "Stock updated successfully"
        return False, "Stock update failed"
    
    except Exception as e:
        return False, f"Error updating stock: {e}"

def get_low_stock_products(producer_id=None):
    """Get products with low stock"""
    try:
        if supabase is None:
            return []
        
        query = supabase.table('products')\
            .select('*')
        
        if producer_id:
            query = query.eq('producer_id', producer_id)
        
        response = query.execute()
        
        if response.data:
            low_stock_products = []
            for product in response.data:
                try:
                    quantity = int(product.get('quantity', 0))
                    min_stock = int(product.get('min_stock', 0))
                    if min_stock > 0 and quantity < min_stock:
                        low_stock_products.append(product)
                except (ValueError, TypeError):
                    continue
            return low_stock_products
        return []
    
    except Exception as e:
        st.error(f"Error fetching low stock products: {e}")
        return []

def get_recent_products(producer_id, limit=5):
    """Get recent products added by producer"""
    try:
        if supabase is None:
            return []
        
        response = supabase.table('products')\
            .select('*')\
            .eq('producer_id', producer_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        st.error(f"Error fetching recent products: {e}")
        return []

# --- Order Functions ---
def get_orders(user_id, role, limit=100):
    """Get orders based on user role"""
    try:
        if supabase is None:
            return []
        
        if role == 'producer':
            field = 'producer_id'
        elif role == 'merchant':
            field = 'merchant_id'
        elif role == 'customer':
            field = 'customer_id'
        else:
            return []
        
        response = supabase.table('orders')\
            .select('*')\
            .eq(field, user_id)\
            .limit(limit)\
            .order('created_at', desc=True)\
            .execute()
        
        if response.data:
            return response.data
        return []
    
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        return []

def get_recent_orders(user_id, role, limit=10):
    """Get recent orders with error handling"""
    try:
        if supabase is None:
            return []
        
        if role == 'producer':
            field = 'producer_id'
        elif role == 'merchant':
            field = 'merchant_id'
        elif role == 'customer':
            field = 'customer_id'
        else:
            return []
        
        response = supabase.table('orders')\
            .select('*')\
            .eq(field, user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        st.error(f"Error fetching recent orders: {e}")
        return []

# --- Dashboard Stats ---
def get_default_stats():
    """Return default stats values"""
    return {
        'total_products': 0,
        'low_stock': 0,
        'total_orders': 0,
        'revenue': 0,
        'total_stock_value': 0,
        'total_investment': 0,
        'potential_profit': 0,
        'pending_revenue': 0,
        'avg_order_value': 0,
        'recent_orders_count': 0,
        'order_status': {},
        'top_products': []
    }

def get_dashboard_stats(role, user_id):
    """Get comprehensive dashboard statistics"""
    try:
        if supabase is None:
            return get_default_stats()
        
        stats = get_default_stats()
        
        if role == 'producer':
            # Get products stats
            products = supabase.table('products')\
                .select('id, quantity, min_stock, price, cost_price')\
                .eq('producer_id', user_id)\
                .execute()
            
            if products.data:
                stats['total_products'] = len(products.data)
                
                # Calculate low stock
                low_stock_count = 0
                total_stock_value = 0
                total_investment = 0
                
                for product in products.data:
                    try:
                        quantity = int(product.get('quantity', 0))
                        min_stock = int(product.get('min_stock', 0))
                        price = float(product.get('price', 0))
                        cost_price = float(product.get('cost_price', 0))
                        
                        if min_stock > 0 and quantity < min_stock:
                            low_stock_count += 1
                        
                        total_stock_value += quantity * price
                        total_investment += quantity * cost_price
                    except (ValueError, TypeError):
                        continue
                
                stats['low_stock'] = low_stock_count
                stats['total_stock_value'] = round(total_stock_value, 2)
                stats['total_investment'] = round(total_investment, 2)
                stats['potential_profit'] = round(total_stock_value - total_investment, 2)
            
            # Get orders stats
            orders = supabase.table('orders')\
                .select('id, total_amount, status, created_at')\
                .eq('producer_id', user_id)\
                .execute()
            
            if orders.data:
                stats['total_orders'] = len(orders.data)
                
                # Status breakdown
                status_counts = {}
                total_revenue = 0
                pending_revenue = 0
                
                for order in orders.data:
                    status = order.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    amount = float(order.get('total_amount', 0))
                    if status == 'delivered':
                        total_revenue += amount
                    elif status in ['pending', 'confirmed']:
                        pending_revenue += amount
                
                stats['revenue'] = round(total_revenue, 2)
                stats['pending_revenue'] = round(pending_revenue, 2)
                stats['order_status'] = status_counts
                
                # Calculate recent orders (last 30 days)
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                recent_orders = [o for o in orders.data if o.get('created_at', '') > thirty_days_ago]
                stats['recent_orders_count'] = len(recent_orders)
                
                # Calculate average order value
                if stats['total_orders'] > 0 and total_revenue > 0:
                    stats['avg_order_value'] = round(total_revenue / stats['total_orders'], 2)
                else:
                    stats['avg_order_value'] = 0
        
        return stats
    
    except Exception as e:
        st.error(f"Error fetching dashboard stats: {e}")
        return get_default_stats()

# Add this function to utils/db_helpers.py

def update_user_profile_image(user_id, image_path):
    """Update user profile image"""
    try:
        if supabase is None:
            return False, "Database connection failed"
        
        response = supabase.table('users')\
            .update({'profile_image': image_path})\
            .eq('id', user_id)\
            .execute()
        
        if response.data:
            return True, "Profile image updated successfully"
        return False, "Profile image update failed"
    
    except Exception as e:
        return False, f"Error updating profile image: {e}"
