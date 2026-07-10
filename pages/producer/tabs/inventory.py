# Add this function to inventory.py for browse products detail view

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
        from utils.db_helpers import get_user_by_id
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

def render_browse_products(user_info):
    """Render the Browse Products sub-tab"""
    
    # Check if showing browse product detail
    if st.session_state.get('show_browse_detail', False) and st.session_state.get('selected_browse_product_id'):
        from utils.db_helpers import get_product_by_id
        selected_product = get_product_by_id(st.session_state.selected_browse_product_id)
        if selected_product:
            render_browse_product_detail(selected_product, user_info)
            return
    
    st.subheader("🔍 Browse Products")
    st.caption("Discover products from other producers on the platform")
    
    # Get all products from all producers (excluding current user's products)
    from utils.db_helpers import get_products
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
                    from utils.db_helpers import get_user_by_id
                    producer = get_user_by_id(producer_id)
                    if producer:
                        producer_cache[producer_id] = producer
                
                if producer_id in producer_cache:
                    producer_info = producer_cache[producer_id]
                    producer_name = producer_info.get('name', 'Unknown')
                    producer_company = producer_info.get('company_name', 'N/A')
                
                # Product Card
                stock = product.get('quantity', 0)
                stock_status = "✅ In Stock" if stock > 0 else "❌ Out of Stock"
                stock_color = "#10b981" if stock > 0 else "#ef4444"
                
                st.markdown(f"""
                <div style="background: #1e293b; border-radius: 10px; padding: 14px 16px; border: 1px solid #334155; margin-bottom: 10px;">
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
