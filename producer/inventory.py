import streamlit as st
import base64
from utils.db_helpers import get_products, create_product, update_product, delete_product

def render_inventory(user_id, user_info):
    """Render inventory tab"""
    st.subheader(" Manage Your Inventory")
    
    # Initialize edit/delete states
    if 'editing_product_id' not in st.session_state:
        st.session_state.editing_product_id = None
    if 'deleting_product_id' not in st.session_state:
        st.session_state.deleting_product_id = None

    # Add Product Form
    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            price = st.number_input("Price (ETB)", min_value=0.01)
            stock = st.number_input("Stock", min_value=0)
            category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"])
            
            uploaded_file = st.file_uploader("Image", type=['jpg', 'png', 'jpeg'])
            img_b64 = None
            if uploaded_file:
                img_b64 = base64.b64encode(uploaded_file.read()).decode()
                st.image(uploaded_file, width=100)
                
            if st.form_submit_button("Add Product"):
                if name:
                    success, msg, _ = create_product(
                        name=name, price=price, stock_quantity=stock, 
                        category=category, producer_id=user_id, image_base64=img_b64
                    )
                    if success: st.success(msg); st.rerun()
                    else: st.error(msg)

    # Display Products
    st.markdown("---")
    st.subheader("Your Products")
    products = get_products(producer_id=user_id)
    
    if products:
        cols = st.columns(3)
        for idx, p in enumerate(products):
            with cols[idx % 3]:
                st.markdown(f"**{p['name']}**")
                st.caption(f"{p.get('price', 0)} ETB | Stock: {p.get('quantity', 0)}")
                
                # Edit/Delete Buttons
                c1, c2 = st.columns(2)
                if c1.button("✏️ Edit", key=f"edit_{p['id']}"):
                    st.session_state.editing_product_id = p['id']
                    st.rerun()
                if c2.button("🗑️ Delete", key=f"del_{p['id']}"):
                    st.session_state.deleting_product_id = p['id']
                    st.rerun()
    else:
        st.info("No products yet.")
