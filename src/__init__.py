# src/__init__.py
"""
AI Engines and Database Layer for the Supply Chain Platform
"""

from . import db
from . import demand_engine
from . import fraud_engine
from . import matching_engine
from . import price_engine
from . import recommendation_engine

# Export database functions
from .db import (
    supabase,
    get_supabase_client,
    get_client,
    init_supabase,
    check_db_connection,
    get_db_status,
    table_exists,
    get_table_count
)

__all__ = [
    'db',
    'demand_engine',
    'fraud_engine',
    'matching_engine',
    'price_engine',
    'recommendation_engine',
    # Database exports
    'supabase',
    'get_supabase_client',
    'get_client',
    'init_supabase',
    'check_db_connection',
    'get_db_status',
    'table_exists',
    'get_table_count'
]
