import streamlit as st
import pandas as pd
import os

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
    st.markdown(f"<h4 style='margin: 10px 0 5px 0; color: #fff; font-size: 16px;'>{product['name']}</h4>", unsafe_allow_html=True)
    
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
    
    # Edit and Delete Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Edit", key=f"edit_{product['id']}", use_container_width=True):
            st.session_state.edit_product_id = product['id']
            st.rerun()
    with col2:
        if st.button("🗑️ Delete", key=f"delete_{product['id']}", use_container_width=True):
            st.session_state.delete_product_id = product['id']
            st.rerun()
    
    # Close product card
    st.markdown('</div>', unsafe_allow_html=True)
