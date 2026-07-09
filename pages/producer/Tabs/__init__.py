"""Tabs package for producer pages"""
from .dashboard import render_dashboard
from .inventory import render_inventory
from .orders import render_orders
from .ai_insights import render_ai_insights

__all__ = ['render_dashboard', 'render_inventory', 'render_orders', 'render_ai_insights']
