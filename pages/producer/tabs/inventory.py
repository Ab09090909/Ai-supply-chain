import streamlit as st
import pandas as pd
from utils.db_helpers import (
    get_products, create_product, update_product, delete_product
)

ETHIOPIAN_CATEGORIES = [
    "Grains & Cereals", "Vegetables", "Fruits",
    "Livestock & Dairy", "Coffee & Tea", "Spices & Herbs", "Other"
]


def render_inventory(user_info, ai):
    st.subheader("📦 Inventory Management")
    user_id = user_info.get('id')
    tab_view, tab_add = st.tabs(["📋 My Products", "➕ Add Product"])
    with tab_add:
        _render_add_product(user_id)
    with tab_view:
        _render_product_list(user_id)


def _render_add_product(user_id):
    with st.form("add_product_form"):
        st.subheader("➕ Add New Product")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name *")
            category = st.selectbox("Category *", ETHIOPIAN_CATEGORIES)
            price = st.number_input("Selling Price (ETB/unit) *", min_value=0.0, step=0.5)
            cost_price = st.number_input("Cost Price (ETB/unit)", min_value=0.0, step=0.5)
        with col2:
            quantity = st.number_input("Stock Quantity *", min_value=0, step=1)
            weight = st.number_input("Unit Weight (kg)", min_value=0.0, step=0.1)
            description = st.text_area("Description", height=120)

        submitted = st.form_submit_button("✅ Add Product", use_container_width=True)
        if submitted:
            if not name or price <= 0:
                st.error("❌ Name and Price are required.")
            else:
                success, msg, _ = create_product(
                    name=name, description=description, category=category,
                    price=price, cost_price=cost_price, stock_quantity=quantity,
                    producer_id=user_id, weight=weight
                )
                if success:
                    st.success(f"✅ '{name}' added!")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")


def _render_product_list(user_id):
    products = get_products(producer_id=user_id)
    if not products:
        st.info("📭 No products yet.")
        return

    df = pd.DataFrame(products)
    cols = [c for c in ['name', 'category', 'price', 'quantity', 'sku'] if c in df.columns]
    st.dataframe(df[cols], use_container_width=True)

    st.markdown("---")
    st.subheader("✏️ Edit / Delete")
    product_map = {p['name']: p for p in products}
    selected = st.selectbox("Select product", list(product_map.keys()))

    if selected:
        p = product_map[selected]
        col1, col2 = st.columns(2)
        with col1:
            with st.form("edit_product_form"):
                new_price = st.number_input("Price (ETB)", value=float(p.get('price', 0)), step=0.5)
                new_qty = st.number_input("Quantity", value=int(p.get('quantity', 0)), step=1)
                new_desc = st.text_area("Description", value=p.get('description', ''))
                if st.form_submit_button("💾 Save", use_container_width=True):
                    ok, msg = update_product(p['id'], price=new_price, quantity=new_qty, description=new_desc)
                    if ok:
                        st.success("✅ Updated!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
        with col2:
            st.warning(f"⚠️ Deleting **{selected}** is permanent.")
            if st.button("🗑️ Delete Product", use_container_width=True):
                ok, msg = delete_product(p['id'])
                if ok:
                    st.success("✅ Deleted!")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
