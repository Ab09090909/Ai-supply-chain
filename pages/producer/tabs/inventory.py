# pages/producer/tabs/inventory.py
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import plotly.express as px

from utils.db_helpers import (
    get_products, create_product, update_product_stock, 
    get_low_stock_products, update_product, delete_product
)

from ..components.product_card import render_product_card

def render_inventory(user_info, ai):
    """Render Professional Inventory Management tab"""
    
    # Custom CSS for professional inventory
    st.markdown("""
    <style>
    /* Inventory Container */
    .inventory-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 4px;
    }
    
    /* Sub-tabs styling */
    .sub-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
        background: #1a1a2e;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #2d3748;
    }
    .sub-tab {
        padding: 10px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.3s ease;
        background: transparent;
        color: #94a3b8;
        border: none;
        flex: 1;
        text-align: center;
    }
    .sub-tab:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #e2e8f0;
    }
    .sub-tab.active {
        background: #667eea;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Stats Cards */
    .stat-card {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #2d3748;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    .stat-card .number {
        font-size: 28px;
        font-weight: 700;
        color: #f8fafc;
    }
    .stat-card .label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    .stat-card .icon {
        font-size: 24px;
        margin-bottom: 4px;
    }
    
    /* Light mode overrides */
    .light-mode .sub-tabs {
        background: #f1f5f9 !important;
        border-color: #e2e8f0 !important;
    }
    .light-mode .sub-tab {
        color: #64748b !important;
    }
    .light-mode .sub-tab:hover {
        background: rgba(102, 126, 234, 0.08) !important;
        color: #1e293b !important;
    }
    .light-mode .sub-tab.active {
        background: #667eea !important;
        color: white !important;
    }
    .light-mode .stat-card {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
    }
    .light-mode .stat-card .number {
        color: #0f172a !important;
    }
    .light-mode .stat-card .label {
        color: #475569 !important;
    }
    
    /* Product Grid */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
        margin-top: 16px;
    }
    
    /* Browse Section */
    .browse-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3748;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .browse-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .browse-card .product-name {
        font-size: 18px;
        font-weight: 600;
        color: #f8fafc;
    }
    .browse-card .product-meta {
        color: #94a3b8;
        font-size: 13px;
        margin: 4px 0;
    }
    .browse-card .product-price {
        color: #10b981;
        font-size: 20px;
        font-weight: 700;
    }
    .browse-card .producer-info {
        background: rgba(102, 126, 234, 0.08);
        padding: 8px 12px;
        border-radius: 8px;
        margin: 8px 0;
        font-size: 13px;
        color: #94a3b8;
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
    .light-mode .browse-card .producer-info {
        background: rgba(102, 126, 234, 0.05) !important;
        color: #475569 !important;
    }
    
    /* Search Bar */
    .search-container {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
        align-items: center;
        flex-wrap: wrap;
    }
    .search-container input {
        flex: 1;
        padding: 10px 16px;
        border-radius: 8px;
        border: 1px solid #2d3748;
        background: #1a1a2e;
        color: #f8fafc;
        font-size: 14px;
        min-width: 200px;
    }
    .search-container input:focus {
        outline: none;
        border-color: #667eea;
    }
    .search-container select {
        padding: 10px 16px;
        border-radius: 8px;
        border: 1px solid #2d3748;
        background: #1a1a2e;
        color: #f8fafc;
        font-size: 14px;
        min-width: 150px;
    }
    .search-container select:focus {
        outline: none;
        border-color: #667eea;
    }
    
    .light-mode .search-container input,
    .light-mode .search-container select {
        background: #ffffff !important;
        color: #1e293b !important;
        border-color: #e2e8f0 !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .sub-tabs {
            flex-direction: column;
        }
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
        .stat-card .number {
            font-size: 22px;
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
    
    st.markdown("""
    <div class="sub-tabs">
        <button class="sub-tab active" onclick="document.getElementById('subtab-my').click()">📦 My Products</button>
        <button class="sub-tab" onclick="document.getElementById('subtab-browse').click()">🔍 Browse Products</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Hidden buttons for sub-tab switching
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 My Products", key="subtab-my", use_container_width=True):
            st.session_state.inventory_subtab = "My Products"
            st.rerun()
    with col2:
        if st.button("🔍 Browse Products", key="subtab-browse", use_container_width=True):
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
    
    # Get all products
    all_products = get_products(producer_id=user_info['id'])
    
    # Stats Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="icon">📦</div>
            <div class="number">{len(all_products)}</div>
            <div class="label">Total Products</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        low_stock = get_low_stock_products(producer_id=user_info['id'])
        st.markdown(f"""
        <div class="stat-card">
            <div class="icon">⚠️</div>
            <div class="number">{len(low_stock)}</div>
            <div class="label">Low Stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if all_products:
            total_value = sum(p.get('price', 0) * p.get('quantity', 0) for p in all_products)
            st.markdown(f"""
            <div class="stat-card">
                <div class="icon">💰</div>
                <div class="number">{total_value:,.0f} ETB</div>
                <div class="label">Stock Value</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="stat-card">
                <div class="icon">💰</div>
                <div class="number">0 ETB</div>
                <div class="label">Stock Value</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if all_products:
            categories = len(set(p.get('category', 'Other') for p in all_products))
            st.markdown(f"""
            <div class="stat-card">
                <div class="icon">📂</div>
                <div class="number">{categories}</div>
                <div class="label">Categories</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="stat-card">
                <div class="icon">📂</div>
                <div class="number">0</div>
                <div class="label">Categories</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check if editing a product
    edit_mode = st.session_state.edit_product_id is not None
    
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
                min_stock = st.number_input("Minimum Stock Alert Level", min_value=1, step=1,
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
                st.image(current_image, width=200)
            
            uploaded_file = st.file_uploader(
                "Upload Product Image" + (" (leave empty to keep current)" if edit_mode else ""),
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            if uploaded_file is not None:
                st.markdown("#### Preview:")
                try:
                    st.image(uploaded_file, caption=f"📷 {uploaded_file.name}", width=300)
                    st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
            
            submitted = st.form_submit_button(
                "💾 Update Product" if edit_mode else "➕ Add Product to Inventory", 
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
    low_stock = get_low_stock_products(producer_id=user_info['id'])
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    # All Products Display
    st.subheader("📦 My Products")
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        
        # Search and Filter
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            search_term = st.text_input("🔍 Search Products", placeholder="Search by name...", key="search_products")
        with col2:
            categories = ["All Categories"] + sorted(list(set(p.get('category', 'Other') for p in all_products)))
            filter_category = st.selectbox("📂 Filter by Category", categories, key="filter_category")
        with col3:
            sort_by = st.selectbox("Sort By", ["Newest", "Price: Low to High", "Price: High to Low", "Stock: Low to High"], key="sort_products")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered_products = all_products.copy()
        
        if search_term:
            filtered_products = [p for p in filtered_products if search_term.lower() in p.get('name', '').lower()]
        
        if filter_category != "All Categories":
            filtered_products = [p for p in filtered_products if p.get('category', 'Other') == filter_category]
        
        # Apply sorting
        if sort_by == "Price: Low to High":
            filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0))
        elif sort_by == "Price: High to Low":
            filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0), reverse=True)
        elif sort_by == "Stock: Low to High":
            filtered_products = sorted(filtered_products, key=lambda x: x.get('quantity', 0))
        # Newest is default (already sorted by created_at desc)
        
        st.caption(f"Showing {len(filtered_products)} of {len(all_products)} products")
        
        st.markdown('<div class="product-grid">', unsafe_allow_html=True)
        
        for product in filtered_products:
            render_product_card(product, user_info)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Delete Confirmation Dialog
        if 'delete_product_id' in st.session_state and st.session_state.delete_product_id:
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
        with st.expander("📋 Detailed Product List", expanded=False):
            display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
            display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
            display_df['Producer'] = user_info.get('name', 'Unknown')
            display_df['Company'] = user_info.get('company_name', 'N/A')
            st.dataframe(display_df, use_container_width=True)
            
            # Export option
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Export to CSV",
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
    
    st.subheader("🔍 Browse Products from Other Producers")
    st.caption("Discover products from other producers on the platform")
    
    # Get all products from all producers (excluding current user's products)
    from utils.db_helpers import get_products
    all_products = get_products()
    
    # Filter out current user's products
    other_products = [p for p in all_products if p.get('producer_id') != user_info['id']]
    
    # Get producer names (we'll fetch them)
    producer_cache = {}
    
    # Search and Filter
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        browse_search = st.text_input("🔍 Search Products", placeholder="Search by name...", key="browse_search")
    with col2:
        categories = ["All Categories"] + sorted(list(set(p.get('category', 'Other') for p in other_products))) if other_products else ["All Categories"]
        browse_category = st.selectbox("📂 Filter by Category", categories, key="browse_category")
    with col3:
        browse_sort = st.selectbox("Sort By", ["Newest", "Price: Low to High", "Price: High to Low"], key="browse_sort")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_products = other_products.copy()
    
    if browse_search:
        filtered_products = [p for p in filtered_products if browse_search.lower() in p.get('name', '').lower()]
    
    if browse_category != "All Categories":
        filtered_products = [p for p in filtered_products if p.get('category', 'Other') == browse_category]
    
    # Apply sorting
    if browse_sort == "Price: Low to High":
        filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0))
    elif browse_sort == "Price: High to Low":
        filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0), reverse=True)
    # Newest is default
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌾 Total Products", len(filtered_products))
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
        # Display products in a grid
        cols = st.columns(3)
        
        for idx, product in enumerate(filtered_products):
            with cols[idx % 3]:
                # Get producer info
                producer_id = product.get('producer_id')
                producer_name = "Unknown Producer"
                producer_company = "N/A"
                
                if producer_id and producer_id not in producer_cache:
                    from utils.db_helpers import get_user_by_id
                    producer = get_user_by_id(producer_id)
                    if producer:
                        producer_cache[producer_id] = producer
                
                if producer_id in producer_cache:
                    producer_info = producer_cache[producer_id]
                    producer_name = producer_info.get('name', 'Unknown')
                    producer_company = producer_info.get('company_name', 'N/A')
                
                # Product Card
                st.markdown(f"""
                <div class="browse-card">
                    <div style="display:flex;justify-content:space-between;align-items:start;">
                        <div>
                            <div class="product-name">{product.get('name', 'Unknown')}</div>
                            <div class="product-meta">📂 {product.get('category', 'N/A')}</div>
                            <div class="product-price">{product.get('price', 0):,.0f} ETB</div>
                            <div class="product-meta">📦 Stock: {product.get('quantity', 0)} units</div>
                        </div>
                        <span style="font-size:40px;">🌾</span>
                    </div>
                    <div class="producer-info">
                        👤 <strong>{producer_name}</strong> • 🏢 {producer_company}
                    </div>
                    <div style="display:flex;gap:8px;margin-top:8px;">
                        <span class="product-info-badge">⚖️ {product.get('weight', 0)} kg</span>
                        <span class="product-info-badge">📅 {pd.to_datetime(product.get('created_at')).strftime('%Y-%m-%d') if product.get('created_at') else 'N/A'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Contact button
                if st.button(f"📞 Contact Producer", key=f"contact_{product.get('id', '')}", use_container_width=True):
                    st.info(f"Contact {producer_name} about {product.get('name', 'this product')}")
        
        st.caption(f"Showing {len(filtered_products)} products from other producers")
        
    else:
        st.info("📭 No products found from other producers. Check back later!")
        
        # Show some suggestions
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Add your own products to get discovered
        - Connect with other producers in your region
        - Browse different categories to find what you need
        """)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_producer_name(producer_id):
    """Get producer name by ID"""
    try:
        from utils.db_helpers import get_user_by_id
        user = get_user_by_id(producer_id)
        if user:
            return user.get('name', 'Unknown Producer')
        return "Unknown Producer"
    except:
        return "Unknown Producer"
