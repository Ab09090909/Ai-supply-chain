import sqlite3
import os
import streamlit as st
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

# Database path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "supply_chain.db")


def ensure_db_directory():
    """Ensure the data directory exists"""
    os.makedirs(DB_DIR, exist_ok=True)


@contextmanager
def get_connection():
    """Context manager for database connections"""
    ensure_db_directory()
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        conn.execute("PRAGMA foreign_keys=ON")   # Enforce foreign keys
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def execute_query(query: str, params: tuple = (), fetch: str = "none"):
    """
    Execute a database query.
    
    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch: 'none' | 'one' | 'all' | 'lastrowid'
    
    Returns:
        Depends on fetch type
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch == "one":
            result = cursor.fetchone()
            conn.commit()
            return dict(result) if result else None
        elif fetch == "all":
            results = cursor.fetchall()
            conn.commit()
            return [dict(row) for row in results]
        elif fetch == "lastrowid":
            conn.commit()
            return cursor.lastrowid
        else:
            conn.commit()
            return cursor.rowcount


def execute_many(query: str, params_list: list):
    """Execute a query with multiple parameter sets"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount


def init_database():
    """Initialize all database tables"""
    ensure_db_directory()
    
    schema = """
    -- ============================================
    -- USERS TABLE
    -- ============================================
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('producer', 'merchant', 'customer', 'admin')),
        phone TEXT DEFAULT '',
        address TEXT DEFAULT '',
        company_name TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1,
        is_verified INTEGER DEFAULT 0,
        last_login TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

    -- ============================================
    -- PRODUCTS TABLE
    -- ============================================
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        category TEXT NOT NULL,
        price REAL NOT NULL CHECK(price > 0),
        cost_price REAL NOT NULL CHECK(cost_price > 0),
        stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK(stock_quantity >= 0),
        min_stock INTEGER DEFAULT 10,
        producer_id INTEGER NOT NULL,
        image_url TEXT DEFAULT '',
        sku TEXT UNIQUE,
        weight REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (producer_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_products_producer ON products(producer_id);
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

    -- ============================================
    -- MERCHANT PRODUCT LISTINGS
    -- ============================================
    CREATE TABLE IF NOT EXISTS merchant_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        listed_price REAL NOT NULL CHECK(listed_price > 0),
        markup_percentage REAL DEFAULT 20.0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (merchant_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        UNIQUE(merchant_id, product_id)
    );

    -- ============================================
    -- ORDERS TABLE
    -- ============================================
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER NOT NULL,
        merchant_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        unit_price REAL NOT NULL CHECK(unit_price > 0),
        total_amount REAL NOT NULL CHECK(total_amount > 0),
        status TEXT NOT NULL DEFAULT 'pending' 
            CHECK(status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
        payment_status TEXT DEFAULT 'unpaid' 
            CHECK(payment_status IN ('unpaid', 'paid', 'refunded')),
        shipping_address TEXT NOT NULL,
        notes TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (customer_id) REFERENCES users(id),
        FOREIGN KEY (merchant_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
    CREATE INDEX IF NOT EXISTS idx_orders_merchant ON orders(merchant_id);
    CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

    -- ============================================
    -- SHIPMENTS TABLE
    -- ============================================
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        carrier TEXT DEFAULT '',
        tracking_number TEXT UNIQUE,
        status TEXT DEFAULT 'pending' 
            CHECK(status IN ('pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'returned')),
        estimated_delivery TEXT,
        actual_delivery TEXT,
        shipping_cost REAL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    );

    -- ============================================
    -- WALLETS TABLE
    -- ============================================
    CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        balance REAL DEFAULT 0.0 CHECK(balance >= 0),
        currency TEXT DEFAULT 'USD',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    -- ============================================
    -- TRANSACTIONS TABLE
    -- ============================================
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('credit', 'debit')),
        amount REAL NOT NULL CHECK(amount > 0),
        description TEXT DEFAULT '',
        reference_id TEXT DEFAULT '',
        balance_after REAL NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
    );

    -- ============================================
    -- REVIEWS TABLE
    -- ============================================
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        order_id INTEGER,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        comment TEXT DEFAULT '',
        is_verified INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        FOREIGN KEY (customer_id) REFERENCES users(id),
        FOREIGN KEY (order_id) REFERENCES orders(id),
        UNIQUE(product_id, customer_id)
    );

    -- ============================================
    -- AI PREDICTIONS LOG
    -- ============================================
    CREATE TABLE IF NOT EXISTS ai_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        input_data TEXT,
        prediction TEXT,
        confidence REAL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    -- ============================================
    -- ACTIVITY LOG
    -- ============================================
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT DEFAULT '',
        ip_address TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id);
    CREATE INDEX IF NOT EXISTS idx_activity_created ON activity_log(created_at);

    -- ============================================
    -- PASSWORD RESET TOKENS
    -- ============================================
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    with get_connection() as conn:
        conn.executescript(schema)
    
    # Insert default admin if not exists
    _seed_default_admin()
    
    st.success("✅ Database initialized successfully!")


def _seed_default_admin():
    """Create default admin user if none exists"""
    from utils.auth import hash_password
    
    admin_exists = execute_query(
        "SELECT id FROM users WHERE role = 'admin' LIMIT 1",
        fetch="one"
    )
    
    if not admin_exists:
        execute_query(
            """INSERT INTO users (name, email, password_hash, role, is_verified)
               VALUES (?, ?, ?, 'admin', 1)""",
            ("System Admin", "admin@supplychain.com", hash_password("Admin@1234")),
            fetch="none"
        )


def get_table_stats() -> dict:
    """Get row counts for all tables"""
    tables = [
        'users', 'products', 'merchant_listings', 'orders',
        'shipments', 'wallets', 'transactions', 'reviews',
        'ai_predictions', 'activity_log'
    ]
    
    stats = {}
    for table in tables:
        try:
            count = execute_query(f"SELECT COUNT(*) as cnt FROM {table}", fetch="one")
            stats[table] = count['cnt'] if count else 0
        except:
            stats[table] = 0
    
    return stats


# Auto-initialize on import
init_database()
