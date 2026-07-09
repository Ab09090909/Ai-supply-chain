import streamlit as st
import pandas as pd
import base64
from utils.db_helpers import get_products, create_product, update_product, delete_product, get_low_stock_products

def render_inventory(user_id, user_info):
    """Render inventory management"""
    st.subheader("📦 Manage Your Inventory")
    
    # Initialize session states
    if 'editing_product_id' not in st.session_state:
        st.session_state.editing_product_id = None
    if 'deleting_product_id' not in st.session_state:
        st.session_state.deleting_product_id = None
    
    # Handle editing
    if st.session_state.editing_product_id:
        _render_edit_form(user_id)
        return
    
    # Handle deleting
    if st.session_state.deleting_product_id:
        _render_delete_confirmation()
        return
    
    # Add new product form
    with st.expander("➕ Add New Product", expanded=False):
        _render_add_product_form(user_id)
    
    st.markdown("---")
    
    # Low stock alerts
    low_stock = get_low_stock_products(producer_id=user_id)
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    # All products
    st.subheader("All Products")
    all_products = get_products(producer_id=user_id)
    
    if all_products:
        cols = st.columns(3)
        
        for idx, product in enumerate(all_products):
            with cols[idx % 3]:
                _render_product_card(product, user_info)
    else:
        st.info("📭 No products yet. Add one above!")

def _render_add_product_form(user_id):
    """Render add product form"""
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            add_name = st.text_input("Product Name")
            add_category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"])
            add_price = st.number_input("Selling Price (ETB)", min_value=0.01)
            add_cost = st.number_input("Cost Price (ETB)", min_value=0.01)
        with col2:
            add_stock = st.number_input("Stock Quantity", min_value=0)
            add_weight = st.number_input("Weight (kg)", min_value=0.0)
            add_desc = st.text_area("Description", height=80)
        
        st.markdown("### 📷 Product Image")
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png', 'webp'])
        
        img_base64 = None
        if uploaded_file:
            img_bytes = uploaded_file.read()
            img_base64 = base64.b64encode(img_bytes).decode()
            st.image(uploaded_file, width=200, caption="Preview")

        if st.form_submit_button("➕ Add Product", type="primary"):
            if add_name:
                success, msg, _ = create_product(
                    name=add_name, description=add_desc, category=add_category,
                    price=add_price, cost_price=add_cost, stock_quantity=add_stock,
                    producer_id=user_id, weight=add_weight, image_base64=img_base64
                )
                if success:
                    st.success(msg)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("❌ Name is required!")

def _render_product_card(product, user_info):
    """Render individual product card"""
    st.markdown("""
    <style>
    .product-card {
        background: #1e293b; border-radius: 12px; padding: 15px;
        border: 1px solid #334155; margin-bottom: 15px;
    }
    .product-image-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 180px; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 10px; overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    
    # Image
    img_b64 = product.get('image_base64')
    if img_b64:
        try:
            img_data = base64.b64decode(img_b64)
            st.image(img_data, use_container_width=True)
        except:
            st.markdown('<div class="product-image-container"><span style="font-size:40px">📦</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="product-image-container"><span style="font-size:40px">📦</span></div>', unsafe_allow_html=True)
    
    # Product info
    st.markdown(f"**{product['name']}**")
    st.caption(f"📂 {product.get('category', 'N/A')} | SKU: {product.get('sku', 'N/A')}")
    st.markdown(f"**{product.get('price', 0):,.2f} ETB**")
    st.caption(f"📦 Stock: {product.get('quantity', 0)} units")
    
    # Additional info
    with st.expander("ℹ️ More Details"):
        st.write(f"**Description:** {product.get('description', 'No description provided.')}")
        st.write(f"**Producer:** {user_info['name']}")
        st.write(f"**Region:** {user_info.get('region', 'N/A')}")
        st.write(f"**Added:** {product.get('created_at', 'N/A')[:10]}")
    
    # Edit/Delete buttons
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✏️ Edit", key=f"edit_btn_{product['id']}", use_container_width=True):
            st.session_state.editing_product_id = product['id']
            st.rerun()
    with col_btn2:
        if st.button("🗑️ Delete", key=f"del_btn_{product['id']}", use_container_width=True):
            st.session_state.deleting_product_id = product['id']
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def _render_edit_form(user_id):
    """Render edit product form"""
    st.warning(f"⚠️ Editing Product ID: {st.session_state.editing_product_id}")
    product_to_edit = next((p for p in get_products(producer_id=user_id) if p['id'] == st.session_state.editing_product_id), None)
    
    if product_to_edit:
        with st.form("edit_product_form"):
            st.markdown("### Edit Product Details")
            col1, col2 = st.columns(2)
            with col1:
                edit_name = st.text_input("Name", value=product_to_edit.get('name', ''))
                edit_price = st.number_input("Price (ETB)", value=float(product_to_edit.get('price', 0)))
                edit_stock = st.number_input("Stock Quantity", value=int(product_to_edit.get('quantity', 0)))
            with col2:
                edit_category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"], 
                                           index=["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"].index(product_to_edit.get('category', 'Grains')))
                edit_cost = st.number_input("Cost Price (ETB)", value=float(product_to_edit.get('cost_price', 0)))
                edit_desc = st.text_area("Description", value=product_to_edit.get('description', ''))
            
            edit_uploaded = st.file_uploader("Upload New Image (Optional)", type=['jpg', 'jpeg', 'png'])
            edit_img_b64 = None
            if edit_uploaded:
                edit_img_b64 = base64.b64encode(edit_uploaded.read()).decode()
                st.image(edit_uploaded, width=150)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                save_edit = st.form_submit_button("💾 Save Changes", type="primary")
            with col_btn2:
                cancel_edit = st.form_submit_button("❌ Cancel")

            if save_edit:
                update_kwargs = {'name': edit_name, 'price': edit_price, 'quantity': edit_stock, 
                                 'category': edit_category, 'cost_price': edit_cost, 'description': edit_desc}
                if edit_img_b64:
                    update_kwargs['image_base64'] = edit_img_b64
                
                if update_product(st.session_state.editing_product_id, **update_kwargs):
                    st.success("✅ Product updated successfully!")
                    st.session_state.editing_product_id = None
                    st.rerun()
                else:
                    st.error("❌ Failed to update product.")
            
            if cancel_edit:
                st.session_state.editing_product_id = None
                st.rerun()

def _render_delete_confirmation():
    """Render delete confirmation"""
    st.error("⚠️ Are you sure you want to delete this product? This action cannot be undone.")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("✅ Yes, Delete It", type="primary"):
            if delete_product(st.session_state.deleting_product_id):
                st.success("✅ Product deleted.")
                st.session_state.deleting_product_id = None
                st.rerun()
    with col_d2:
        if st.button("❌ No, Keep It"):
            st.session_state.deleting_product_id = None
            st.rerun()
