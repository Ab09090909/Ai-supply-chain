# pages/producer/components/__init__.py
"""Components package for producer pages"""
from .profile import render_profile, render_edit_profile
from .product_card import render_product_card, render_product_detail

__all__ = ['render_profile', 'render_edit_profile', 'render_product_card', 'render_product_detail']
