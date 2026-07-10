# pages/producer/components/product_card.py
import streamlit as st
import pandas as pd
import os
from utils.db_helpers import get_user_by_id

def render_product_card(product, user_info):
    """Render a product card with image, info, and action buttons"""
    
    # Product Card Container
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    
    # Display product image if exists
    image_url = product.get('image_url')
    image_displayed = False
    if image_url:
        try:
            if os.path.exists(image_url):
                st.image(image_url, use_container_width=True)
                image_displayed = True
        except Exception as e:
            pass
    
    # Show placeholder if no image
    if not image_displayed:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 150px; border-radius: 8px;
                    display: flex; align-items: center; justify-content: center;
                    margin-bottom: 10px;">
            <span style="color: white; font-size: 48px;">📦</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Product Name
    st.markdown(f"<h4 style='margin: 10px 0 5px 0; color: #fff; font-size: 16px;'>{product.get('name', 'Unknown')}</h4>", unsafe_allow_html=True)
    
    # Producer Information
    st.markdown(f"""
    <div class="producer-info">
        <strong>👤 Producer:</strong> {user_info.get('name', 'Unknown')}<br>
        <strong>🏢 Company:</strong> {user_info.get('company_name', 'N/A')}<br>
        <strong>📞 Contact:</strong> {user_info.get('phone', 'N/A')}
    </div>
    """, unsafe_allow_html=True)
    
    # Product Information
    st.markdown(f"""
    <p style="margin: 5px 0; color: #94a3b8; font-size: 13px;">📂 {product.get('category', 'N/A')}</p>
    <p style="margin: 5px 0; color: #10b981; font-weight: bold; font-size: 18px;">{product.get('price', 0)} ETB</p>
    <p style="margin: 5px 0; color: #f59e0b; font-size: 13px;">📦 Stock: {product.get('quantity', 0)} units</p>
    <p style="margin: 5px 0; color: #64748b; font-size: 12px;">SKU: {product.get('sku', 'N/A')}</p>
    """, unsafe_allow_html=True)
    
    # Product Info Badges
    created_date = pd.to_datetime(product.get('created_at')).strftime('%Y-%m-%d') if product.get('created_at') else 'N/A'
    st.markdown(f"""
    <div style="margin-top: 8px;">
        <span class="product-info-badge">⚖️ {product.get('weight', 0)} kg</span>
        <span class="product-info-badge">📅 {created_date}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👁️ View", key=f"view_{product.get('id', '')}", use_container_width=True):
            st.session_state.selected_product_id = product.get('id')
            st.session_state.show_product_detail = True
            st.rerun()
    with col2:
        if st.button("✏️ Edit", key=f"edit_{product.get('id', '')}", use_container_width=True):
            st.session_state.edit_product_id = product.get('id')
            st.rerun()
    with col3:
        if st.button("🗑️ Delete", key=f"delete_{product.get('id', '')}", use_container_width=True):
            st.session_state.delete_product_id = product.get('id')
            st.rerun()
    
    # Close product card
    st.markdown('</div>', unsafe_allow_html=True)


def render_product_detail(product, user_info):
    """Render detailed product view with order functionality"""
    
    if not product:
        return
    
    st.markdown("---")
    st.markdown(f"## 📦 {product.get('name', 'Product Details')}")
    
    # Get producer info from database if available
    producer_id = product.get('producer_id')
    producer_data = user_info  # Default to current user
    
    # If product has a different producer, fetch their info
    if producer_id and producer_id != user_info.get('id'):
        fetched_producer = get_user_by_id(producer_id)
        if fetched_producer:
            producer_data = fetched_producer
    
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
        stock_status = "✅ In Stock" if stock > 0 else "❌ Out of Stock"
        
        detail_html = f"""
        <div style="background: #1a1a2e; padding: 20px; border-radius: 12px; border: 1px solid #2d3748;">
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
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #2d3748;">
                <span style="color: #94a3b8; font-size: 12px;">Status</span>
                <p style="color: {'#10b981' if stock > 0 else '#ef4444'}; font-weight: 600; margin: 2px 0;">
                    {stock_status}
                </p>
            </div>
        </div>
        """
        st.markdown(detail_html, unsafe_allow_html=True)
    
    # Producer Information
    st.markdown("### 👤 Producer Information")
    
    producer_name = producer_data.get('name', 'Unknown')
    producer_company = producer_data.get('company_name', 'N/A')
    producer_phone = producer_data.get('phone', 'N/A')
    producer_region = producer_data.get('region', 'N/A')
    producer_address = producer_data.get('address', 'N/A')
    
    producer_html = f"""
    <div style="background: #1a1a2e; padding: 16px 20px; border-radius: 12px; border: 1px solid #2d3748; margin: 8px 0;">
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
    """
    st.markdown(producer_html, unsafe_allow_html=True)
    
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
                help=f"Available stock: {stock_available} units"
            )
        
        with col2:
            total_price = quantity * product.get('price', 0)
            price_html = f"""
            <div style="background: #1a1a2e; padding: 12px 16px; border-radius: 8px; border: 1px solid #2d3748; margin-top: 20px;">
                <span style="color: #94a3b8; font-size: 12px;">Total Price</span>
                <p style="color: #10b981; font-weight: 700; font-size: 20px; margin: 2px 0;">{total_price:,.2f} ETB</p>
                <span style="color: #94a3b8; font-size: 11px;">{quantity} x {product.get('price', 0)} ETB</span>
            </div>
            """
            st.markdown(price_html, unsafe_allow_html=True)
        
        with col3:
            if st.button("🛒 Place Order", use_container_width=True, type="primary"):
                if product.get('quantity', 0) >= quantity:
                    st.success(f"✅ Order placed successfully for {quantity} units of {product.get('name')}!")
                    st.info("📋 Order details have been sent to the producer.")
                    st.balloons()
                else:
                    st.error(f"❌ Insufficient stock! Available: {product.get('quantity', 0)} units")
    
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
    if st.button("🔙 Back to Products", use_container_width=True):
        st.session_state.show_product_detail = False
        st.session_state.selected_product_id = None
        st.rerun()
