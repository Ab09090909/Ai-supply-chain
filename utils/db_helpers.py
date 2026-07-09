import streamlit as st
from src.db import execute_query, execute_many
from utils.auth import hash_password, verify_password, generate_session_token
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uuid


# =====================================================
# USER OPERATIONS
# =====================================================

def create_user(name: str, email: str, password: str, role: str, 
                phone: str = "", company_name: str = "") -> tuple:
    """Create a new user with wallet"""
    try:
        # Check if email exists
        existing = execute_query(
            "SELECT id FROM users WHERE email = ?", (email,), fetch="one"
        )
        if existing:
            return False, "Email already registered", None
        
        password_hash = hash_password(password)
        
        user_id = execute_query(
            """INSERT INTO users (name, email, password_hash, role, phone, company_name, is_verified)
               VALUES (?, ?, ?, ?, ?, ?, 1)""",
            (name, email, password_hash, role, phone, company_name),
            fetch="lastrowid"
        )
        
        # Create wallet for the user
        execute_query(
            "INSERT INTO wallets (user_id, balance) VALUES (?, 0.0)",
            (user_id,), fetch="none"
        )
        
        # Log activity
        log_activity(user_id, "account_created", f"New {role} account created")
        
        return True, "Account created successfully!", user_id
    
    except Exception as e:
        return False, f"Error creating account: {str(e)}", None


def authenticate_user(email: str, password: str) -> tuple:
    """Authenticate user and return user info"""
    try:
        user = execute_query(
            "SELECT * FROM users WHERE email = ? AND is_active = 1",
            (email,), fetch="one"
        )
        
        if not user:
            return False, "Invalid email or password", None
        
        if not verify_password(password, user['password_hash']):
            return False, "Invalid email or password", None
        
        # Update last login
        execute_query(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?",
            (user['id'],), fetch="none"
        )
        
        # Log activity
        log_activity(user['id'], "login", "User logged in")
        
        # Return safe user info (no password hash)
        user_info = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'phone': user['phone'],
            'company_name': user['company_name'],
            'session_token': generate_session_token()
        }
        
        return True, "Login successful!", user_info
    
    except Exception as e:
        return False, f"Authentication error: {str(e)}", None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    return execute_query(
        "SELECT id, name, email, role, phone, company_name, is_active, created_at FROM users WHERE id = ?",
        (user_id,), fetch="one"
    )


def get_all_users(role: str = None, limit: int = 100) -> List[Dict]:
    """Get all users, optionally filtered by role"""
    if role:
        return execute_query(
            "SELECT id, name, email, role, phone, is_active, created_at FROM users WHERE role = ? ORDER BY created_at DESC LIMIT ?",
            (role, limit), fetch="all"
        )
    return execute_query(
        "SELECT id, name, email, role, phone, is_active, created_at FROM users ORDER BY created_at DESC LIMIT ?",
        (limit,), fetch="all"
    )


def update_user(user_id: int, **kwargs) -> bool:
    """Update user fields"""
    allowed_fields = {'name', 'phone', 'address', 'company_name', 'is_active'}
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    set_clause += ", updated_at = datetime('now')"
    values = list(updates.values()) + [user_id]
    
    execute_query(f"UPDATE users SET {set_clause} WHERE id = ?", tuple(values))
    return True


def delete_user(user_id: int) -> bool:
    """Soft delete user (set inactive)"""
    execute_query(
        "UPDATE users SET is_active = 0, updated_at = datetime('now') WHERE id = ?",
        (user_id,)
    )
    log_activity(user_id, "account_deactivated", "User account deactivated")
    return True


# =====================================================
# PRODUCT OPERATIONS
# =====================================================

def create_product(name: str, description: str, category: str, price: float,
                   cost_price: float, stock_quantity: int, producer_id: int,
                   weight: float = 0) -> tuple:
    """Create a new product"""
    try:
        sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        
        product_id = execute_query(
            """INSERT INTO products 
               (name, description, category, price, cost_price, stock_quantity, producer_id, sku, weight)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, description, category, price, cost_price, stock_quantity, producer_id, sku, weight),
            fetch="lastrowid"
        )
        
        log_activity(producer_id, "product_created", f"Product '{name}' created (SKU: {sku})")
        return True, "Product created successfully!", product_id
    
    except Exception as e:
        return False, f"Error creating product: {str(e)}", None


def get_products(producer_id: int = None, category: str = None, 
                 active_only: bool = True, limit: int = 100) -> List[Dict]:
    """Get products with optional filters"""
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if producer_id:
        query += " AND producer_id = ?"
        params.append(producer_id)
    if category:
        query += " AND category = ?"
        params.append(category)
    if active_only:
        query += " AND is_active = 1"
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    return execute_query(query, tuple(params), fetch="all")


def update_product_stock(product_id: int, quantity_change: int) -> bool:
    """Update product stock (positive to add, negative to subtract)"""
    product = execute_query("SELECT stock_quantity FROM products WHERE id = ?", (product_id,), fetch="one")
    if not product:
        return False
    
    new_stock = product['stock_quantity'] + quantity_change
    if new_stock < 0:
        return False
    
    execute_query(
        "UPDATE products SET stock_quantity = ?, updated_at = datetime('now') WHERE id = ?",
        (new_stock, product_id)
    )
    return True


def get_low_stock_products(producer_id: int = None) -> List[Dict]:
    """Get products below minimum stock level"""
    if producer_id:
        return execute_query(
            """SELECT * FROM products 
               WHERE stock_quantity <= min_stock AND is_active = 1 AND producer_id = ?
               ORDER BY stock_quantity ASC""",
            (producer_id,), fetch="all"
        )
    return execute_query(
        """SELECT * FROM products 
           WHERE stock_quantity <= min_stock AND is_active = 1
           ORDER BY stock_quantity ASC""",
        fetch="all"
    )


# =====================================================
# ORDER OPERATIONS
# =====================================================

def create_order(customer_id: int, merchant_id: int, product_id: int,
                 quantity: int, unit_price: float, shipping_address: str,
                 notes: str = "") -> tuple:
    """Create a new order"""
    try:
        # Check stock
        product = execute_query("SELECT stock_quantity FROM products WHERE id = ?", (product_id,), fetch="one")
        if not product or product['stock_quantity'] < quantity:
            return False, "Insufficient stock", None
        
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        total_amount = unit_price * quantity
        
        order_id = execute_query(
            """INSERT INTO orders 
               (order_number, customer_id, merchant_id, product_id, quantity, unit_price, total_amount, shipping_address, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_number, customer_id, merchant_id, product_id, quantity, unit_price, total_amount, shipping_address, notes),
            fetch="lastrowid"
        )
        
        # Reduce stock
        update_product_stock(product_id, -quantity)
        
        log_activity(customer_id, "order_created", f"Order {order_number} created")
        return True, f"Order {order_number} created successfully!", order_id
    
    except Exception as e:
        return False, f"Error creating order: {str(e)}", None


def get_orders(user_id: int, role: str, status: str = None, limit: int = 50) -> List[Dict]:
    """Get orders for a user based on their role"""
    query = """
        SELECT o.*, 
               p.name as product_name,
               c.name as customer_name,
               m.name as merchant_name
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.id
        LEFT JOIN users c ON o.customer_id = c.id
        LEFT JOIN users m ON o.merchant_id = m.id
        WHERE 1=1
    """
    params = []
    
    if role == 'customer':
        query += " AND o.customer_id = ?"
        params.append(user_id)
    elif role == 'merchant':
        query += " AND o.merchant_id = ?"
        params.append(user_id)
    elif role == 'producer':
        query += " AND p.producer_id = ?"
        params.append(user_id)
    
    if status:
        query += " AND o.status = ?"
        params.append(status)
    
    query += " ORDER BY o.created_at DESC LIMIT ?"
    params.append(limit)
    
    return execute_query(query, tuple(params), fetch="all")


def update_order_status(order_id: int, new_status: str) -> bool:
    """Update order status"""
    valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
    if new_status not in valid_statuses:
        return False
    
    execute_query(
        "UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (new_status, order_id)
    )
    return True


# =====================================================
# WALLET OPERATIONS
# =====================================================

def get_wallet_balance(user_id: int) -> float:
    """Get user's wallet balance"""
    wallet = execute_query(
        "SELECT balance FROM wallets WHERE user_id = ?", (user_id,), fetch="one"
    )
    return wallet['balance'] if wallet else 0.0


def wallet_transaction(user_id: int, amount: float, trans_type: str, description: str = "") -> bool:
    """Process wallet transaction (credit or debit)"""
    wallet = execute_query("SELECT * FROM wallets WHERE user_id = ?", (user_id,), fetch="one")
    if not wallet:
        return False
    
    if trans_type == 'debit' and wallet['balance'] < amount:
        return False
    
    if trans_type == 'credit':
        new_balance = wallet['balance'] + amount
    else:
        new_balance = wallet['balance'] - amount
    
    execute_query(
        "UPDATE wallets SET balance = ?, updated_at = datetime('now') WHERE user_id = ?",
        (new_balance, user_id)
    )
    
    execute_query(
        """INSERT INTO transactions (wallet_id, type, amount, description, balance_after)
           VALUES (?, ?, ?, ?, ?)""",
        (wallet['id'], trans_type, amount, description, new_balance)
    )
    
    return True


def get_transaction_history(user_id: int, limit: int = 20) -> List[Dict]:
    """Get transaction history for a user"""
    return execute_query(
        """SELECT t.* FROM transactions t
           JOIN wallets w ON t.wallet_id = w.id
           WHERE w.user_id = ?
           ORDER BY t.created_at DESC LIMIT ?""",
        (user_id, limit), fetch="all"
    )


# =====================================================
# ACTIVITY LOG
# =====================================================

def log_activity(user_id: int, action: str, details: str = ""):
    """Log user activity"""
    try:
        execute_query(
            "INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, action, details)
        )
    except:
        pass  # Don't fail main operation if logging fails


def get_activity_log(user_id: int = None, limit: int = 50) -> List[Dict]:
    """Get activity log"""
    if user_id:
        return execute_query(
            """SELECT a.*, u.name as user_name FROM activity_log a
               LEFT JOIN users u ON a.user_id = u.id
               WHERE a.user_id = ?
               ORDER BY a.created_at DESC LIMIT ?""",
            (user_id, limit), fetch="all"
        )
    return execute_query(
        """SELECT a.*, u.name as user_name FROM activity_log a
           LEFT JOIN users u ON a.user_id = u.id
           ORDER BY a.created_at DESC LIMIT ?""",
        (limit,), fetch="all"
    )


# =====================================================
# DASHBOARD ANALYTICS
# =====================================================

def get_dashboard_stats(role: str, user_id: int) -> Dict:
    """Get dashboard statistics based on role"""
    stats = {}
    
    if role == 'producer':
        stats['total_products'] = execute_query(
            "SELECT COUNT(*) as cnt FROM products WHERE producer_id = ? AND is_active = 1",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['low_stock'] = execute_query(
            "SELECT COUNT(*) as cnt FROM products WHERE producer_id = ? AND stock_quantity <= min_stock",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['total_orders'] = execute_query(
            """SELECT COUNT(*) as cnt FROM orders o 
               JOIN products p ON o.product_id = p.id WHERE p.producer_id = ?""",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['revenue'] = execute_query(
            """SELECT COALESCE(SUM(o.total_amount), 0) as total FROM orders o 
               JOIN products p ON o.product_id = p.id 
               WHERE p.producer_id = ? AND o.status NOT IN ('cancelled', 'refunded')""",
            (user_id,), fetch="one"
        )['total']
    
    elif role == 'merchant':
        stats['active_listings'] = execute_query(
            "SELECT COUNT(*) as cnt FROM merchant_listings WHERE merchant_id = ? AND is_active = 1",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['total_orders'] = execute_query(
            "SELECT COUNT(*) as cnt FROM orders WHERE merchant_id = ?",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['pending_orders'] = execute_query(
            "SELECT COUNT(*) as cnt FROM orders WHERE merchant_id = ? AND status = 'pending'",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['revenue'] = execute_query(
            """SELECT COALESCE(SUM(total_amount), 0) as total FROM orders 
               WHERE merchant_id = ? AND status NOT IN ('cancelled', 'refunded')""",
            (user_id,), fetch="one"
        )['total']
    
    elif role == 'customer':
        stats['total_orders'] = execute_query(
            "SELECT COUNT(*) as cnt FROM orders WHERE customer_id = ?",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['active_orders'] = execute_query(
            """SELECT COUNT(*) as cnt FROM orders 
               WHERE customer_id = ? AND status NOT IN ('delivered', 'cancelled', 'refunded')""",
            (user_id,), fetch="one"
        )['cnt']
        
        stats['total_spent'] = execute_query(
            """SELECT COALESCE(SUM(total_amount), 0) as total FROM orders 
               WHERE customer_id = ? AND status NOT IN ('cancelled', 'refunded')""",
            (user_id,), fetch="one"
        )['total']
        
        stats['wallet_balance'] = get_wallet_balance(user_id)
    
    elif role == 'admin':
        stats['total_users'] = execute_query("SELECT COUNT(*) as cnt FROM users WHERE is_active = 1", fetch="one")['cnt']
        stats['total_products'] = execute_query("SELECT COUNT(*) as cnt FROM products WHERE is_active = 1", fetch="one")['cnt']
        stats['total_orders'] = execute_query("SELECT COUNT(*) as cnt FROM orders", fetch="one")['cnt']
        stats['total_revenue'] = execute_query(
            "SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE status NOT IN ('cancelled', 'refunded')",
            fetch="one"
        )['total']
    
    return stats
