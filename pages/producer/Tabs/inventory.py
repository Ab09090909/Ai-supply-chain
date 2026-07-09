import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

from utils.db_helpers import (
    get_products, create_product, update_product_stock, 
    get_low_stock_products, update_product, delete_product
)

from ..components.product_card import render_product_card

def render_inventory(user_info, ai):
    """Render Inventory Management tab"""
    st.subheader("Manage Your Inventory")
    
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
    st.subheader("All Products")
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        
        st.markdown("### 📦 Product Gallery")
        cols = st.columns(3)
        
        for idx, product in enumerate(all_products):
            with cols[idx % 3]:
                render_product_card(product, user_info)
        
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
        st.markdown("---")
        st.markdown("### 📋 Detailed Product List")
        display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
        display_df['Producer'] = user_info.get('name', 'Unknown')
        display_df['Company'] = user_info.get('company_name', 'N/A')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("📭 No products added yet. Click 'Add New Product' above to get started!")
