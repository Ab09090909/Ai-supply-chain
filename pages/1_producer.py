# ==========================================
# TAB 2: INVENTORY MANAGEMENT
# ==========================================
with tab_inventory:
    st.subheader("Manage Your Inventory")
    
    # Add Product Form
    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name", placeholder="e.g., Teff, Coffee")
                category = st.selectbox("Category", ["Grains", "Vegetables", "Fruits", "Dairy", "Meat", "Other"])
                price = st.number_input("Selling Price (ETB)", min_value=0.01, step=0.01)
                cost_price = st.number_input("Cost Price (ETB)", min_value=0.01, step=0.01)
            
            with col2:
                stock = st.number_input("Initial Stock Quantity", min_value=0, step=1)
                min_stock = st.number_input("Minimum Stock Alert Level", min_value=1, value=10)
                weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
                description = st.text_area("Description", placeholder="Brief product description...", height=80)
            
            # Image Upload Section
            st.markdown("---")
            st.markdown("### 📷 Product Image")
            uploaded_file = st.file_uploader(
                "Upload Product Image",
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            if uploaded_file is not None:
                # Display preview
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(uploaded_file, caption="Product Image Preview", use_container_width=True)
                    st.success(f"✅ Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            submitted = st.form_submit_button("➕ Add Product", use_container_width=True, type="primary")
            
            if submitted:
                if not name:
                    st.error("Product name is required!")
                else:
                    # Handle image upload
                    image_path = None
                    if uploaded_file is not None:
                        try:
                            # Create uploads directory if it doesn't exist
                            os.makedirs("uploads/products", exist_ok=True)
                            
                            # Generate unique filename
                            import uuid
                            file_extension = uploaded_file.name.split('.')[-1].lower()
                            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                            image_path = os.path.join("uploads/products", unique_filename)
                            
                            # Save the file
                            with open(image_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            st.success(f"✅ Image saved successfully!")
                        except Exception as e:
                            st.error(f"Error saving image: {e}")
                            image_path = None
                    
                    # Create product with or without image
                    success, msg, prod_id = create_product(
                        name=name, 
                        description=description, 
                        category=category,
                        price=price, 
                        cost_price=cost_price, 
                        stock_quantity=stock,
                        producer_id=user_info['id'], 
                        weight=weight,
                        image_url=image_path  # Pass image path
                    )
                    
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("---")
    
    # Low Stock Alerts
    low_stock = get_low_stock_products(producer_id=user_info['id'])
    if low_stock:
        st.warning(f"⚠️ **{len(low_stock)} products are below minimum stock level!**")
        df_low = pd.DataFrame(low_stock)
        st.dataframe(df_low[['name', 'category', 'quantity', 'min_stock']], use_container_width=True)
    
    # All Products Table with Images
    st.subheader("All Products")
    all_products = get_products(producer_id=user_info['id'])
    
    if all_products:
        df_all = pd.DataFrame(all_products)
        
        # Display products in a more visual way
        st.markdown("### Product Gallery")
        
        # Create columns for product cards
        cols = st.columns(3)
        
        for idx, product in enumerate(all_products):
            with cols[idx % 3]:
                # Product Card
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                            padding: 15px; border-radius: 12px; margin-bottom: 15px; 
                            border: 1px solid #475569;">
                    <div style="text-align: center; margin-bottom: 10px;">
                """, unsafe_allow_html=True)
                
                # Display product image if exists
                image_url = product.get('image_url')
                if image_url and os.path.exists(image_url):
                    st.image(image_url, use_container_width=True)
                else:
                    # Placeholder for no image
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                height: 150px; border-radius: 8px;
                                display: flex; align-items: center; justify-content: center;
                                margin-bottom: 10px;">
                        <p style="color: white; font-size: 48px; margin: 0;">📦</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Product Info
                st.markdown(f"""
                <div style="text-align: left;">
                    <h4 style="margin: 10px 0 5px 0; color: #fff;">{product['name']}</h4>
                    <p style="margin: 0; color: #94a3b8; font-size: 13px;">📂 {product['category']}</p>
                    <p style="margin: 5px 0; color: #10b981; font-weight: bold; font-size: 16px;">
                        {product['price']} ETB
                    </p>
                    <p style="margin: 5px 0; color: #f59e0b; font-size: 13px;">
                        📦 Stock: {product['quantity']} units
                    </p>
                    <p style="margin: 5px 0; color: #64748b; font-size: 12px;">
                        SKU: {product.get('sku', 'N/A')}
                    </p>
                </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Also show detailed table
        st.markdown("---")
        st.markdown("### Detailed Product List")
        display_df = df_all[['name', 'category', 'price', 'quantity', 'sku', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No products added yet.")
