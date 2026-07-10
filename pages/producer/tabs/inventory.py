# pages/producer/tabs/inventory.py
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import plotly.express as px

from utils.db_helpers import (
    get_products, create_product, update_product_stock, 
    get_low_stock_products, update_product, delete_product, get_product_by_id, get_user_by_id
)

from ..components.product_card import render_product_card, render_product_detail

# ==========================================
# RENDER BROWSE PRODUCT DETAIL
# ==========================================
def render_browse_product_detail(product, user_info):
    """Render detailed view for browsed products with order functionality"""
    
    if not product:
        return
    
    st.markdown("---")
    st.markdown(f"## 📦 {product.get('name', 'Product Details')}")
    
    # Product Image
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image_url = product.get('image_url')
        if image_url and os.path.exists(image_url):
            st.image(image_url, use_container_width=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        height: 250px; border-radius: 12px;
                        display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 64px;">📦</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        stock = product.get('quantity', 0)
        stock_color = "#f59e0b" if stock > 0 else "#ef4444"
        
        st.markdown(f"""
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
            <h3 style="color: #f8fafc; margin-top: 0;">{product.get('name', 'Unknown')}</h3>
            <p style="color: #94a3b8; font-size: 14px;">{product.get('description', 'No description available')}</p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0;">
                <div>
                    <span style="color: #94a3b8; font-size: 12px;">Category</span>
                    <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{product.get('category', 'N/A')}</p>
                </div>
                <div>
                    <span style="color: #94a3b8; font-size: 12px;">Price</span>
                    <p style="color: #10b981; font-weight: 700; font-size: 20px; margin: 2px 0;">{product.get('price', 0)} ETB</p>
                </div>
                <div>
                    <span style="color: #94a3b8; font-size: 12px;">Stock</span>
                    <p style="color: {stock_color}; font-weight: 600; margin: 2px 0;">{stock} units</p>
                </div>
                <div>
                    <span style="color: #94a3b8; font-size: 12px;">Weight</span>
                    <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{product.get('weight', 0)} kg</p>
                </div>
                <div>
                    <span style="color: #94a3b8; font-size: 12px;">SKU</span>
                    <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{product.get('sku', 'N/A')}</p>
                </div>
                <div>
                    <span style="color: #94a3b8; font-size: 12px;">Added</span>
                    <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{pd.to_datetime(product.get('created_at')).strftime('%Y-%m-%d') if product.get('created_at') else 'N/A'}</p>
                </div>
            </div>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #334155;">
                <span style="color: #94a3b8; font-size: 12px;">Status</span>
                <p style="color: {'#10b981' if stock > 0 else '#ef4444'}; font-weight: 600; margin: 2px 0;">
                    {'✅ In Stock' if stock > 0 else '❌ Out of Stock'}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Get producer info for browsed product
    producer_id = product.get('producer_id')
    producer_name = "Unknown Producer"
    producer_company = "N/A"
    producer_phone = "N/A"
    producer_region = "N/A"
    producer_address = "N/A"
    
    if producer_id:
        producer = get_user_by_id(producer_id)
        if producer:
            producer_name = producer.get('name', 'Unknown')
            producer_company = producer.get('company_name', 'N/A')
            producer_phone = producer.get('phone', 'N/A')
            producer_region = producer.get('region', 'N/A')
            producer_address = producer.get('address', 'N/A')
    
    # Producer Information
    st.markdown("### 👤 Producer Information")
    st.markdown(f"""
    <div style="background: #1e293b; padding: 16px 20px; border-radius: 12px; border: 1px solid #334155; margin: 8px 0;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <div>
                <span style="color: #94a3b8; font-size: 12px;">Name</span>
                <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{producer_name}</p>
            </div>
            <div>
                <span style="color: #94a3b8; font-size: 12px;">Company</span>
                <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{producer_company}</p>
            </div>
            <div>
                <span style="color: #94a3b8; font-size: 12px;">Phone</span>
                <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{producer_phone}</p>
            </div>
            <div>
                <span style="color: #94a3b8; font-size: 12px;">Region</span>
                <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{producer_region}</p>
            </div>
            <div style="grid-column: span 2;">
                <span style="color: #94a3b8; font-size: 12px;">Address</span>
                <p style="color: #f8fafc; font-weight: 600; margin: 2px 0;">{producer_address}, {producer_region}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Order Section
    st.markdown("### 🛒 Order This Product")
    st.markdown("---")
    
    stock_available = product.get('quantity', 0)
    
    if stock_available <= 0:
        st.error("❌ This product is currently out of stock. Please check back later.")
    else:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            max_quantity = max(1, stock_available)
            quantity = st.number_input(
                "Quantity", 
                min_value=1, 
                max_value=max_quantity, 
                value=1, 
                step=1,
                help=f"Available stock: {stock_available} units",
                key="browse_quantity"
            )
        
        with col2:
            total_price = quantity * product.get('price', 0)
            st.markdown(f"""
            <div style="background: #1e293b; padding: 12px 16px; border-radius: 8px; border: 1px solid #334155; margin-top: 20px;">
                <span style="color: #94a3b8; font-size: 12px;">Total Price</span>
                <p style="color: #10b981; font-weight: 700; font-size: 20px; margin: 2px 0;">{total_price:,.2f} ETB</p>
                <span style="color: #94a3b8; font-size: 11px;">{quantity} x {product.get('price', 0)} ETB</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div style="margin-top: 16px;">', unsafe_allow_html=True)
            if st.button("🛒 Place Order", use_container_width=True, type="primary", key="browse_order"):
                if product.get('quantity', 0) >= quantity:
                    st.success(f"✅ Order placed successfully for {quantity} units of {product.get('name')}!")
                    st.info("📋 Order details have been sent to the producer.")
                    st.balloons()
                else:
                    st.error(f"❌ Insufficient stock! Available: {product.get('quantity', 0)} units")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Terms and Conditions
    with st.expander("📋 Terms & Conditions", expanded=False):
        st.markdown("""
        **Order Agreement:**
        
        1. **Order Confirmation**: All orders are subject to confirmation by the producer.
        2. **Payment Terms**: Payment must be made upon delivery or as agreed with the producer.
        3. **Delivery**: Delivery timelines will be communicated by the producer.
        4. **Quality Assurance**: Products must meet the quality standards described.
        5. **Returns**: Returns are subject to the producer's return policy.
        6. **Contact**: For any inquiries, please contact the producer directly.
        """)
    
    # Back button
    if st.button("🔙 Back to Browse", use_container_width=True):
        st.session_state.show_browse_detail = False
        st.session_state.selected_browse_product_id = None
        st.rerun()


def render_inventory(user_info, ai):
    """Render Professional Inventory Management tab"""
    
    # Custom CSS with improved dark mode colors
    st.markdown("""
    <style>
    /* Inventory Container */
    .inventory-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2px;
    }
    
    /* Stats Row - Single Compact Row */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 12px;
        background: #1e293b;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .stat-item {
        text-align: center;
        padding: 4px 0;
    }
    .stat-item .number {
        font-size: 22px;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    .stat-item .number.green { color: #10b981; }
    .stat-item .number.red { color: #ef4444; }
    .stat-item .number.blue { color: #667eea; }
    .stat-item .number.gold { color: #f59e0b; }
    .stat-item .label {
        font-size: 10px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 1px;
        font-weight: 500;
    }
    .stat-item .icon {
        font-size: 16px;
        display: block;
        margin-bottom: 2px;
    }
    
    /* Light Mode Stats */
    .light-mode .stats-row {
        background: #f1f5f9 !important;
        border-color: #e2e8f0 !important;
    }
    .light-mode .stat-item .number {
        color: #0f172a !important;
    }
    .light-mode .stat-item .label {
        color: #475569 !important;
    }
    
    /* Search Bar - Improved */
    .search-container {
        display: flex;
        gap: 8px;
        margin-bottom: 10px;
        align-items: center;
        flex-wrap: wrap;
        background: #1e293b;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .search-container input {
        flex: 1;
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid #334155;
        background: #0f172a;
        color: #f8fafc;
        font-size: 13px;
        min-width: 150px;
    }
    .search-container input::placeholder {
        color: #64748b;
    }
    .search-container input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    .search-container select {
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid #334155;
        background: #0f172a;
        color: #f8fafc;
        font-size: 13px;
        min-width: 120px;
    }
    .search-container select:focus {
        outline: none;
        border-color: #667eea;
    }
    
    .light-mode .search-container {
        background: #f1f5f9 !important;
        border-color: #e2e8f0 !important;
    }
    .light-mode .search-container input,
    .light-mode .search-container select {
        background: #ffffff !important;
        color: #1e293b !important;
        border-color: #e2e8f0 !important;
    }
    .light-mode .search-container input::placeholder {
        color: #94a3b8 !important;
    }
    
    /* Product Grid */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 12px;
        margin-top: 10px;
    }
    
    /* Browse Cards */
    .browse-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid #334155;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .browse-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    .light-mode .browse-card {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
    }
    .light-mode .browse-card .product-name {
        color: #0f172a !important;
    }
    .light-mode .browse-card .product-meta {
        color: #475569 !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .product-grid {
            grid-template-columns: 1fr;
        }
        .search-container {
            flex-direction: column;
        }
        .search-container input,
        .search-container select {
            width: 100%;
        }
        .stats-row {
            grid-template-columns: repeat(2, 1fr);
            gap: 4px;
        }
        .stat-item .number {
            font-size: 18px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check theme mode for light/dark styling
    theme_class = "light-mode" if st.session_state.get('theme_mode') == 'light' else ""
    
    st.markdown(f'<div class="inventory-container {theme_class}">', unsafe_allow_html=True)
    
    # ==========================================
    # SUB-TABS
    # ==========================================
    if 'inventory_subtab' not in st.session_state:
        st.session_state.inventory_subtab = "My Products"
    
    # Custom sub-tab buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 My Products", key="subtab-my", use_container_width=True, 
                    type="primary" if st.session_state.inventory_subtab == "My Products" else "secondary"):
            st.session_state.inventory_subtab = "My Products"
            st.rerun()
    with col2:
        if st.button("🔍 Browse Products", key="subtab-browse", use_container_width=True,
                    type="primary" if st.session_state.inventory_subtab == "Browse Products" else "secondary"):
            st.session_state.inventory_subtab = "Browse Products"
            st.rerun()
    
    st.markdown("---")
    
    # ==========================================
    # SUB-TAB: MY PRODUCTS
    # ==========================================
    if st.session_state.inventory_subtab == "My Products":
        render_my_products(user_info, ai)
    
    # ==========================================
    # SUB-TAB: BROWSE PRODUCTS
    # ==========================================
    else:
        render_browse_products(user_info)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# RENDER MY PRODUCTS
# ==========================================
def render_my_products(user_info, ai):
    """Render the My Products sub-tab"""
    
    # Check if showing product detail
    if st.session_state.get('show_product_detail', False) and st.session_state.get('selected_product_id'):
        all_products = get_products(producer_id=user_info['id'])
        selected_product = next((p for p in all_products if p['id'] == st.session_state.selected_product_id), None)
        if selected_product:
            render_product_detail(selected_product, user_info)
            return
    
    # Get all products
    all_products = get_products(producer_id=user_info['id'])
    low_stock = get_low_stock_products(producer_id=user_info['id'])
    
    # Calculate stats
    total_products = len(all_products)
    low_stock_count = len(low_stock)
    total_value = sum(p.get('price', 0) * p.get('quantity', 0) for p in all_products) if all_products else 0
    categories_count = len(set(p.get('category', 'Other') for p in all_products)) if all_products else 0
    
    # ==========================================
    # COMPACT STATS ROW - All in One Row
    # ==========================================
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-item">
            <span class="icon">📦</span>
            <div class="number blue">{total_products}</div>
            <div class="label">Products</div>
        </div>
        <div class="stat-item">
            <span class="icon">⚠️</span>
            <div class="number {'red' if low_stock_count > 0 else 'green'}">{low_stock_count}</div>
            <div class="label">Low Stock</div>
        </div>
        <div class="stat-item">
            <span class="icon">💰</span>
            <div class="number gold">{total_value:,.0f}</div>
            <div class="label">Stock Value</div>
        </div>
        <div class="stat-item">
            <span class="icon">📂</span>
            <div class="number blue">{categories_count}</div>
            <div class="label">Categories</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if editing a product
    edit_mode = st.session_state.get('edit_product_id') is not None
    
    # Add/Edit Product Form
    with st.expander("➕ Add New Product" if not edit_mode else "✏️ Edit Product", expanded=edit_mode):
        with st.form("add_product_form"):
            # If in edit mode, load product data
            product_data = None
            if edit_mode:
                all_products = get_products(producer_id=user_info['id'])
                product_data = next((p for p in all_products if p['id'] == st.session_state.edit_product_id), None)
            
            col1, col2 = st.columns(2)
            
            with col1:
                name_input = st.text_input("Product Name", placeholder="e.g., Teff, Coffee", 
                                          value=product_data['name'] if product_data else "")
                category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Coffee", "Other"],
                                       index=["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Coffee", "Other"].index(product_data['category']) if product_data and product_data.get('category') in ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Coffee", "Other"] else 0)
                price = st.number_input("Selling Price (ETB)", min_value=0.01, step=0.01,
                                       value=float(product_data['price']) if product_data else 0.01)
                cost_price = st.number_input("Cost Price (ETB)", min_value=0.01, step=0.01,
                                            value=float(product_data['cost_price']) if product_data and product_data.get('cost_price') else 0.01)
            
            with col2:
                stock = st.number_input("Stock Quantity", min_value=0, step=1,
                                       value=int(product_data['quantity']) if product_data else 0)
                min_stock = st.number_input("Min Stock Alert", min_value=1, step=1,
                                           value=int(product_data.get('min_stock', 10)) if product_data else 10)
                weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1,
                                        value=float(product_data.get('weight', 0)) if product_data else 0.0)
                description = st.text_area("Description", placeholder="Brief product description...", height=80,
                                          value=product_data.get('description', '') if product_data else "")
            
            # Image Upload Section
            st.markdown("---")
            st.markdown("### 📷 Product Image")
            current_image = product_data.get('image_url') if product_data else None
            
            if current_image and os.path.exists(current_image):
                st.markdown("#### Current Image:")
                st.image(current_image, width=150)
            
            uploaded_file = st.file_uploader(
                "Upload Product Image" + (" (leave empty to keep current)" if edit_mode else ""),
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            if uploaded_file is not None:
                st.markdown("#### Preview:")
                try:
                    st.image(uploaded_file, caption=f"📷 {uploaded_file.name}", width=250)
                    st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
            
            submitted = st.form_submit_button(
                "💾 Update Product" if edit_mode else "➕ Add Product", 
                use_container_width=True, type="primary"
            )
            
            if submitted:
                if not name_input:
                    st.error("❌ Product name is required!")
                else:
                    image_path = current_image
                    if uploaded_file is not None:
                        try:
                            os.makedirs("uploads/products", exist_ok=True)
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                            image_path = os.path.join("uploads/products", unique_filename)
                            
                            with open(image_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            st.success(f"✅ Image saved: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"Error saving image: {e}")
                            image_path = current_image
                    
                    if edit_mode:
                        try:
                            success, msg = update_product(
                                product_id=st.session_state.edit_product_id,
                                name=name_input,
                                description=description,
                                category=category,
                                price=price,
                                cost_price=cost_price,
                                stock_quantity=stock,
                                min_stock=min_stock,
                                weight=weight,
                                image_url=image_path
                            )
                            
                            if success:
                                # Update AI knowledge
                                product_info = {
                                    'id': st.session_state.edit_product_id,
                                    'name': name_input,
                                    'category': category,
                                    'price': price,
                                    'cost_price': cost_price,
                                    'quantity': stock,
                                    'weight': weight
                                }
                                ai.analyze_product(product_info)
                                
                                st.success(f"✅ {msg}")
                                st.session_state.edit_product_id = None
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                        except Exception as e:
                            st.error(f"❌ Error updating product: {e}")
                    else:
                        success, msg, prod_id = create_product(
                            name=name_input, 
                            description=description, 
                            category=category,
                            price=price, 
                            cost_price=cost_price, 
                            stock_quantity=stock,
                            producer_id=user_info['id'], 
                            weight=weight,
                            image_url=image_path
                        )
                        
                        if success:
                            # Update AI knowledge
                            product_info = {
                                'id': prod_id,
                                'name': name_input,
                                'category': category,
                                'price': price,
                                'cost_price': cost_price,
                                'quantity': stock,
                                'weight': weight
                            }
                            ai.analyze_product(product_info)
                            
                            st.success(f"✅ {msg}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

    st.markdown("---")
    
    # Low Stock Alerts
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    # All Products Display
    st.subheader("📦 My Products")
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        
        # Search and Filter - Improved
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 1.5])
        with col1:
            search_term = st.text_input("🔍 Search", placeholder="Search by name...", key="search_products", label_visibility="collapsed")
        with col2:
            categories = ["All"] + sorted(list(set(p.get('category', 'Other') for p in all_products)))
            filter_category = st.selectbox("📂 Category", categories, key="filter_category", label_visibility="collapsed")
        with col3:
            sort_by = st.selectbox("Sort", ["Newest", "Price: Low", "Price: High", "Stock: Low"], key="sort_products", label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered_products = all_products.copy()
        
        if search_term:
            filtered_products = [p for p in filtered_products if search_term.lower() in p.get('name', '').lower()]
        
        if filter_category != "All":
            filtered_products = [p for p in filtered_products if p.get('category', 'Other') == filter_category]
        
        # Apply sorting
        if sort_by == "Price: Low":
            filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0))
        elif sort_by == "Price: High":
            filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0), reverse=True)
        elif sort_by == "Stock: Low":
            filtered_products = sorted(filtered_products, key=lambda x: x.get('quantity', 0))
        
        st.caption(f"Showing {len(filtered_products)} of {len(all_products)} products")
        
        st.markdown('<div class="product-grid">', unsafe_allow_html=True)
        
        for product in filtered_products:
            render_product_card(product, user_info)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Delete Confirmation Dialog
        if st.session_state.get('delete_product_id'):
            product_to_delete = next((p for p in all_products if p['id'] == st.session_state.delete_product_id), None)
            if product_to_delete:
                st.warning(f"⚠️ Are you sure you want to delete '{product_to_delete['name']}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", use_container_width=True):
                        try:
                            success, msg = delete_product(st.session_state.delete_product_id)
                            if success:
                                st.success(f"✅ {msg}")
                                st.session_state.delete_product_id = None
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")
                        except Exception as e:
                            st.error(f"❌ Error deleting product: {e}")
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.delete_product_id = None
                        st.rerun()
        
        # Detailed Table View
        with st.expander("📋 Detailed List", expanded=False):
            display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
            display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
            display_df['Producer'] = user_info.get('name', 'Unknown')
            display_df['Company'] = user_info.get('company_name', 'N/A')
            st.dataframe(display_df, use_container_width=True)
            
            # Export option
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Export CSV",
                data=csv,
                file_name=f"products_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("📭 No products added yet. Click 'Add New Product' above to get started!")


# ==========================================
# RENDER BROWSE PRODUCTS
# ==========================================
def render_browse_products(user_info):
    """Render the Browse Products sub-tab"""
    
    # Check if showing browse product detail
    if st.session_state.get('show_browse_detail', False) and st.session_state.get('selected_browse_product_id'):
        selected_product = get_product_by_id(st.session_state.selected_browse_product_id)
        if selected_product:
            render_browse_product_detail(selected_product, user_info)
            return
    
    st.subheader("🔍 Browse Products")
    st.caption("Discover products from other producers on the platform")
    
    # Get all products from all producers (excluding current user's products)
    all_products = get_products()
    
    # Filter out current user's products
    other_products = [p for p in all_products if p.get('producer_id') != user_info['id']]
    
    # Producer cache
    producer_cache = {}
    
    # Search and Filter - Improved
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 2, 1.5])
    with col1:
        browse_search = st.text_input("🔍 Search", placeholder="Search by name...", key="browse_search", label_visibility="collapsed")
    with col2:
        categories = ["All"] + sorted(list(set(p.get('category', 'Other') for p in other_products))) if other_products else ["All"]
        browse_category = st.selectbox("📂 Category", categories, key="browse_category", label_visibility="collapsed")
    with col3:
        browse_sort = st.selectbox("Sort", ["Newest", "Price: Low", "Price: High"], key="browse_sort", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_products = other_products.copy()
    
    if browse_search:
        filtered_products = [p for p in filtered_products if browse_search.lower() in p.get('name', '').lower()]
    
    if browse_category != "All":
        filtered_products = [p for p in filtered_products if p.get('category', 'Other') == browse_category]
    
    # Apply sorting
    if browse_sort == "Price: Low":
        filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0))
    elif browse_sort == "Price: High":
        filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0), reverse=True)
    
    # Stats - Compact
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌾 Products", len(filtered_products))
    with col2:
        if filtered_products:
            avg_price = sum(p.get('price', 0) for p in filtered_products) / len(filtered_products)
            st.metric("💰 Avg Price", f"{avg_price:,.0f} ETB")
        else:
            st.metric("💰 Avg Price", "N/A")
    with col3:
        if filtered_products:
            categories_count = len(set(p.get('category', 'Other') for p in filtered_products))
            st.metric("📂 Categories", categories_count)
        else:
            st.metric("📂 Categories", "0")
    
    st.markdown("---")
    
    if filtered_products:
        cols = st.columns(3)
        
        for idx, product in enumerate(filtered_products):
            with cols[idx % 3]:
                # Get producer info
                producer_id = product.get('producer_id')
                producer_name = "Unknown Producer"
                producer_company = "N/A"
                
                if producer_id and producer_id not in producer_cache:
                    producer = get_user_by_id(producer_id)
                    if producer:
                        producer_cache[producer_id] = producer
                
                if producer_id in producer_cache:
                    producer_info = producer_cache[producer_id]
                    producer_name = producer_info.get('name', 'Unknown')
                    producer_company = producer_info.get('company_name', 'N/A')
                
                stock = product.get('quantity', 0)
                stock_color = "#10b981" if stock > 0 else "#ef4444"
                stock_status = "✅ In Stock" if stock > 0 else "❌ Out of Stock"
                
                # Product Card
                st.markdown(f"""
                <div class="browse-card">
                    <div style="display:flex;justify-content:space-between;align-items:start;">
                        <div>
                            <div style="font-size: 16px; font-weight: 600; color: #f8fafc;">{product.get('name', 'Unknown')}</div>
                            <div style="color: #94a3b8; font-size: 12px; margin: 2px 0;">📂 {product.get('category', 'N/A')}</div>
                            <div style="color: #10b981; font-size: 18px; font-weight: 700;">{product.get('price', 0):,.0f} ETB</div>
                            <div style="color: #94a3b8; font-size: 12px;">📦 Stock: {stock} units</div>
                            <div style="color: {stock_color}; font-size: 12px; font-weight: 500;">{stock_status}</div>
                        </div>
                        <span style="font-size:32px;">🌾</span>
                    </div>
                    <div style="background: rgba(102, 126, 234, 0.08); padding: 6px 10px; border-radius: 6px; margin: 6px 0; font-size: 12px; color: #94a3b8;">
                        👤 <strong style="color: #e2e8f0;">{producer_name}</strong> • 🏢 {producer_company}
                    </div>
                    <div style="display:flex;gap:6px;margin-top:6px; flex-wrap: wrap;">
                        <span style="display:inline-block; background: #334155; padding: 2px 10px; border-radius: 12px; font-size: 11px; color: #e2e8f0;">⚖️ {product.get('weight', 0)} kg</span>
                        <span style="display:inline-block; background: #334155; padding: 2px 10px; border-radius: 12px; font-size: 11px; color: #e2e8f0;">📅 {pd.to_datetime(product.get('created_at')).strftime('%Y-%m-%d') if product.get('created_at') else 'N/A'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # View Details Button
                if st.button("👁️ View Details", key=f"browse_view_{product.get('id', '')}", use_container_width=True):
                    st.session_state.selected_browse_product_id = product.get('id')
                    st.session_state.show_browse_detail = True
                    st.rerun()
        
        st.caption(f"Showing {len(filtered_products)} products from other producers")
        
    else:
        st.info("📭 No products found from other producers. Check back later!")
        
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Add your own products to get discovered
        - Connect with other producers in your region
        - Browse different categories to find what you need
        """)
